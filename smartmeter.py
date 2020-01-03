import datetime
import os
import signal
import time
import traceback
from copy import deepcopy

import toml
from sshtunnel import SSHTunnelForwarder

import electric_meter
import setup_logging
from smartmeter_telegrambot import SmartmeterBot

CONFIGDATEI = "smartmeter_cfg_vorlage.toml"
DEMANDDATEI = "demand_cfg.toml"
FEHLERDATEI = "fehler_smartmeter.log"
SKRIPTPFAD = os.path.abspath(os.path.dirname(__file__))


def load_config():
    """
    Lädt die Konfiguration aus dem smartmeter_cfg_vorlage.toml File
    :return:
    """
    configfile = os.path.join(SKRIPTPFAD, CONFIGDATEI)
    with open(configfile) as conffile:
        config = toml.loads(conffile.read())
    config["ssh"] = {}
    with open(config["pg"]["pfad_zu_ssh_auth"]) as confsshfile:
        config["ssh"] = toml.loads(confsshfile.read())
    return config


LOGGER = setup_logging.create_logger("smartmeter", 20)
CONFIG = load_config()

DAUER_SCHNELLINTERVALL = CONFIG["pg"]["dauer_schnellintervall"]
SCHNELLINTERVALL = CONFIG["pg"]["schnellintervall"]


class MessHandler:
    """
    Klasse zuständig für das organiesieren, dass Messwerte ausgelesen, gespeichert und in die Datenbank
    geschrieben werden.
    """
    def __init__(self, messregister):
        self.schnelles_messen = False
        self.startzeit_schnelles_messen = False
        self.messregister = messregister
        self.messregister_save = deepcopy(messregister)
        self.messwerte_liste = []
        self.intervall_daten_senden = CONFIG["pg"]["intervall_daten_senden"]

    def set_schnelles_messintervall(self, *_):
        """
        Kommt von außerhalb das Signal USR2 wird das Mess und Sendeintervall verkürzt
        """
        self.schnelles_messen = True
        self.startzeit_schnelles_messen = datetime.datetime.now()
        for key in self.messregister:
            self.messregister[key]["intervall"] = SCHNELLINTERVALL
        self.intervall_daten_senden = SCHNELLINTERVALL

    def off_schnelles_messintervall(self):
        """
        Mess und Sendeintervall wird wieder auf Standardwerte zurückgesetzt
        :return:
        """
        messintervall = deepcopy(self.messregister_save)
        for key in self.messregister:
            self.messregister[key]["intervall"] = messintervall[key]["intervall"]
        self.schnelles_messen = False
        self.intervall_daten_senden = CONFIG["pg"]["intervall_daten_senden"]

    def add_messwerte(self, messwerte):
        """
        Speichern der Messwerte bis zu Ihrer Übertragung
        :param messwerte: list
        :return:
        """
        self.messwerte_liste.append(messwerte)

    def write_messwerte(self, pg_handler):
        """
        Gespeicherte Messwerte werden nach Aufbau eines SSH Tunnels in die Datenbank geschrieben
        :return:
        """
        LOGGER.debug("Sende Daten")
        pg_handler.daten_schreiben(self.messwerte_liste)
        self.messwerte_liste = []


class PGHandler:
    """
    Zuständige Klasse für die Eintragungen in die PostGreSQL Datenbank
    """
    def __init__(self, port):
        self.pguser = CONFIG["pg"]["pguser"]
        self.pgpw = CONFIG["pg"]["pgpw"]
        self.port = port
        self.db = CONFIG["pg"]["db"]
        self.connection = None
        self.connect_db()

    def __del__(self):
        self.close_db()

    def connect_db(self):
        self.connection = psycopg2.connect(dbname=self.db, user=self.pguser, password=self.pgpw,
                                           port=self.port, host="localhost")

    def close_db(self):
        self.connection.close()

    def daten_schreiben(self, daten_liste):
        """
        Daten werden in die Datenbank geschrieben
        Spalten und Values werden analysiert und SQL String aufbereitet
        :param daten_liste:
        :return:
        """
        with self.connection.cursor() as curs:
            for daten in daten_liste:
                values = []
                spalte_liste = []
                for spalte, wert in daten.items():
                    values.append(wert)
                    spalte_liste.append(spalte)
                values_var = ', '.join(['%s'] * (len(spalte_liste)))
                spalten = ", ".join(spalte_liste)
                sql = "INSERT INTO smartmeter ({spalten}) VALUES ({values_var})".format(spalten=spalten,
                                                                                        values_var=values_var)
                try:
                    curs.execute(sql, values)
                except psycopg2.IntegrityError:
                    LOGGER.warning("duplicate key value vorhanden - ignorieren")
                    self.connection.rollback()
                else:
                    self.connection.commit()


def set_messzeitpunkt(messregister, zeitpunkt=datetime.datetime.now().replace(microsecond=0)-datetime.timedelta(days=1),
                      messauftrag=None):
    """
    Setzten des letzten Zeitpunktes, wann die Messwerte ausgelesen worden sind
    Wird kein zeitpunkt übergeben, so wird von der aktuellen Zeit ein Tag zurückgerechnet. Dies ist für die
    erste Ausführung erforderlich, damit sofort mit dem Messen begonnen wird.
    :param messregister:
    :param zeitpunkt:
    :param messauftrag:
    :return:
    """
    for key in messregister:
        if messauftrag is not None and key not in messauftrag:
            continue
        messregister[key]["messzeitpunkt"] = zeitpunkt


def create_auszulesende_messregister(messregister, now):
    """
    Prüft welche Messwerte nach Ihren Intervalleinstellungen im aktuellen Durchlauf ausgelesen werden müssen
    :param messregister:
    :param now:
    :return:
    """
    return [key for key in messregister if
            (now - messregister[key]["messzeitpunkt"]).total_seconds() >= messregister[key]["intervall"]]


def erzeuge_messregister():
    """
    Erzeugt das messregister nach dem Start des Skriptes, abhängig der Konfigurationseinstellungen, in die passende
    Struktur.
    :return:
    """
    messregister = {}
    for key, value in CONFIG["messintervall"][0].items():
        messregister[key] = {}
        messregister[key]["intervall"] = value
    return messregister


def change_holding_register():
    """Eventuell zukünftige Funktion zum schreiben der Demand Werte in die Register des Smartmeters"""
    pass


def fehlermeldung_schreiben(fehlermeldung):
    """
    Schreibt nicht abgefangene Fehlermeldungen in eine sperate Datei, um so leichter Fehlermeldungen ausfindig machen zu
    können welche noch Abgefangen werden müssen.
    :param fehlermeldung:
    :return:
    """
    with open(os.path.join(SKRIPTPFAD, FEHLERDATEI), "a") as file:
        file.write(fehlermeldung)


def main():
    messregister = erzeuge_messregister()
    set_messzeitpunkt(messregister)
    messhandler = MessHandler(messregister)
    telegram_bot = SmartmeterBot(CONFIG["telegram_bot"]["token"], LOGGER)

    # SIGUSR1 beschreibt die Holding Register mit den eingestellten werden in der Config Datei
    # SIGUSR2 setzt das schnelle Messintervall
    signal.signal(signal.SIGUSR1, change_holding_register)
    signal.signal(signal.SIGUSR2, messhandler.set_schnelles_messintervall)
    smartmeter = electric_meter.SDM530(serial_if=CONFIG["modbus"]["serial_if"],
                                       serial_if_baud=CONFIG["modbus"]["serial_if_baud"],
                                       serial_if_byte=CONFIG["modbus"]["serial_if_byte"],
                                       serial_if_par=CONFIG["modbus"]["serial_if_par"],
                                       serial_if_stop=CONFIG["modbus"]["serial_if_stop"],
                                       slave_addr=CONFIG["modbus"]["slave_addr"],
                                       logger=LOGGER)
    zeitpunkt_daten_gesendet = datetime.datetime.now()
    with SSHTunnelForwarder(
            (CONFIG["ssh"]["ip_server"], CONFIG["ssh"]["ssh_port"]), ssh_username=CONFIG["ssh"]["user"],
            ssh_password=CONFIG["ssh"]["pw"], remote_bind_address=('127.0.0.1', CONFIG["pg"]["pgport"])) as server:
        pg_handler = PGHandler(server.local_bind_port)
        while True:
            now = datetime.datetime.now()
            now = now.replace(microsecond=0)

            # Prüfen ob schnelles Messen aktiv ist und ob dies wieder auf Standard zurück gesetzt werden muss
            if messhandler.schnelles_messen:
                if (now - messhandler.startzeit_schnelles_messen).total_seconds() > DAUER_SCHNELLINTERVALL:
                    messhandler.off_schnelles_messintervall()
            else:
                telegram_bot.get_updates()

            # Prüfe welche Messwerte auszulesen sind
            messauftrag = create_auszulesende_messregister(messregister, now)

            # Messauftrag abarbeiten und Zeitpunk ergänzen
            if messauftrag:
                start_messen = datetime.datetime.now()
                messwerte = smartmeter.read_input_values(messauftrag)
                LOGGER.info("Messdauer: {}".format(datetime.datetime.now() - start_messen))
                messwerte["ts"] = now
                messhandler.add_messwerte(messwerte)
                set_messzeitpunkt(messregister, now, messauftrag)

            # Schreibe die Messdaten in die Datenbank nach eingestellten Intervall
            if (now - zeitpunkt_daten_gesendet).total_seconds() > messhandler.intervall_daten_senden:
                start_schreiben = datetime.datetime.now()
                messhandler.write_messwerte(pg_handler)
                LOGGER.info("DB Dauer schreiben: {}".format(datetime.datetime.now() - start_schreiben))
                zeitpunkt_daten_gesendet = now
            LOGGER.info("Durchlaufdauer: {}".format(datetime.datetime.now() - now))
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    finally:
        fehlermeldung_schreiben(traceback.format_exc())
        LOGGER.exception("Schwerwiegender Fehler aufgetreten")
