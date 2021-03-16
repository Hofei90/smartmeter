import datetime
import os
import signal
import time
import traceback
from copy import deepcopy
from sys import exit

import toml

import electric_meter
import setup_logging
import db_model as db
import db_postgrest_model as db_postgrest


CONFIGDATEI = "smartmeter_cfg.toml"
FEHLERDATEI = "fehler_smartmeter.log"
SKRIPTPFAD = os.path.abspath(os.path.dirname(__file__))


def load_config():
    """Lädt die Konfiguration aus dem smartmeter_cfg.toml File"""
    configfile = os.path.join(SKRIPTPFAD, CONFIGDATEI)
    with open(configfile) as conffile:
        config = toml.loads(conffile.read())
    return config


LOGGER = setup_logging.create_logger("smartmeter", 20)
CONFIG = load_config()

if CONFIG["telegram_bot"]["token"]:
    from smartmeter_telegrambot import SmartmeterBot


class MessHandler:
    """
    MessHandler ist zuständig für das organiesieren, dass Messwerte ausgelesen, gespeichert und in die Datenbank
    geschrieben werden.
    """
    def __init__(self, messregister):
        self.schnelles_messen = False
        self.startzeit_schnelles_messen = datetime.datetime(1970, 1, 1)
        self.messregister = messregister
        self.messregister_save = deepcopy(messregister)
        self.messwerte_liste = []
        self.intervall_daten_senden = CONFIG["mess_cfg"]["intervall_daten_senden"]
        self.pausenzeit = CONFIG["mess_cfg"]["messintervall"]

    def set_schnelles_messintervall(self, *_):
        """Kommt von außerhalb das Signal USR2 wird das Mess und Sendeintervall verkürzt"""
        self.schnelles_messen = True
        self.startzeit_schnelles_messen = datetime.datetime.now()
        self.intervall_daten_senden = CONFIG["mess_cfg"]["schnelles_messintervall"]
        self.pausenzeit = CONFIG["mess_cfg"]["schnelles_messintervall"]

    def off_schnelles_messintervall(self):
        """Mess und Sendeintervall wird wieder auf Standardwerte zurückgesetzt"""
        self.schnelles_messen = False
        self.startzeit_schnelles_messen = datetime.datetime(1970, 1, 1)
        self.intervall_daten_senden = CONFIG["mess_cfg"]["intervall_daten_senden"]
        self.pausenzeit = CONFIG["mess_cfg"]["messintervall"]

    def add_messwerte(self, messwerte):
        """Speichern der Messwerte zwischen bis zu Ihrer Übertragung"""
        self.messwerte_liste.append(messwerte)

    def schreibe_messwerte(self, datenbankschnittstelle):
        """Gespeicherte Messwerte in die Datenbank geschrieben"""
        LOGGER.debug("Sende Daten")
        datenbankschnittstelle.insert_many(self.messwerte_liste)
        self.messwerte_liste = []

    def erstelle_auszulesende_messregister(self):
        """Prüft welche Messwerte nach Ihren Intervalleinstellungen im aktuellen Durchlauf ausgelesen werden müssen"""
        if self.schnelles_messen:
            return [key for key in self.messregister]
        else:
            return [key for key in self.messregister if self.messregister[key]["verbleibender_durchlauf"] <= 1]

    def reduziere_durchlauf_anzahl(self):
        for key in self.messregister:
            self.messregister[key]["verbleibender_durchlauf"] -= 1

    def durchlauf_zuruecksetzen(self, messauftrag):
        for key in messauftrag:
            self.messregister[key]["verbleibender_durchlauf"] = deepcopy(self.messregister[key]["intervall"])


class Datenbankschnittstelle:
    def __init__(self, db_adapter):
        self.db_adapter = db_adapter
        if db_adapter == "postgrest":
            self.headers = {f"Authorization": "{user} {token}".format(user=CONFIG["db"]["postgrest"]["user"],
                                                                      token=CONFIG["db"]["postgrest"]["token"])}
            url = CONFIG["db"]["postgrest"]["url"]
            if not url.endswith("/"):
                url = f"{url}/"
            self.url = "{url}{table}".format(url=url,
                                             table=CONFIG["db"]["postgrest"]["table"])
            self.none_messdaten = self.__none_messdaten_dictionary_erstellen()
        else:
            self.headers = None
            self.url = None
            db_adapter = CONFIG["db"]["db"]
            db_ = db.init_db(CONFIG["db"][db_adapter]["database"], db_adapter, CONFIG["db"].get(db_adapter))
            db.DB_PROXY.initialize(db_)
            db.create_tables()

    def insert_many(self, daten):
        if self.db_adapter == "postgrest":
            db_postgrest.sende_daten(self.url, self.headers, daten, self.none_messdaten, LOGGER)
        else:
            db.insert_many(daten)

    @staticmethod
    def __none_messdaten_dictionary_erstellen():
        none_daten = {"ts": None}
        for key in CONFIG["durchlaufintervall"]:
            none_daten[key.lower()] = None
        return none_daten


def schreibe_config(config, configfile):
    with open(configfile, "a", encoding="UTF-8") as file:
        file.write(f"# Nach dem wievielten Durchläuf der jeweilige Wert ausgelesen werden soll \n"
                   f"# Ausschalten mit false\n"
                   f"# Einträge werden automatisch nach dem ersten Start erstellt, Config anschließend nochmal prüfen\n"
                   f"{toml.dumps(config)}")
    LOGGER.info("Durchlaufintervall in Config aktualisiert \n Programm wird beendet. Bitte neu starten")
    global nofailure
    nofailure = True
    exit(0)


def erzeuge_durchlaufintervall(smartmeter):
    register = smartmeter.get_input_keys()
    durchlaufintervall = {}
    for key in register:
        durchlaufintervall[key] = 1
    config = {"durchlaufintervall": durchlaufintervall}
    schreibe_config(config, CONFIGDATEI)


def erzeuge_messregister(smartmeter):
    """Erzeugt das messregister nach dem Start des Skriptes"""
    if "durchlaufintervall" in CONFIG:
        messregister = {}
        for key, value in CONFIG["durchlaufintervall"].items():
            if value:
                messregister[key] = {}
                messregister[key]["intervall"] = value
                messregister[key]["verbleibender_durchlauf"] = 0
        return messregister
    else:
        erzeuge_durchlaufintervall(smartmeter)


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
    device = electric_meter.get_device_list().get(CONFIG["mess_cfg"]["device"])
    smartmeter = device(serial_if=CONFIG["modbus"]["serial_if"],
                        serial_if_baud=CONFIG["modbus"]["serial_if_baud"],
                        serial_if_byte=CONFIG["modbus"]["serial_if_byte"],
                        serial_if_par=CONFIG["modbus"]["serial_if_par"],
                        serial_if_stop=CONFIG["modbus"]["serial_if_stop"],
                        slave_addr=CONFIG["modbus"]["slave_addr"],
                        logger=LOGGER)

    messregister = erzeuge_messregister(smartmeter)
    messhandler = MessHandler(messregister)

    datenbankschnittstelle = Datenbankschnittstelle(CONFIG["db"]["db"])

    if CONFIG["telegram_bot"]["token"]:
        telegram_bot = SmartmeterBot(CONFIG["telegram_bot"]["token"], LOGGER)
    else:
        telegram_bot = None

    # SIGUSR2 setzt das schnelle Messintervall
    signal.signal(signal.SIGUSR2, messhandler.set_schnelles_messintervall)

    zeitpunkt_daten_gesendet = datetime.datetime(1970, 1, 1)
    start_messzeitpunkt = datetime.datetime(1970, 1, 1)

    LOGGER.info("Initialisierung abgeschlossen - Start Messungen")

    while True:
        now = datetime.datetime.now()
        now = now.replace(microsecond=0)

        # Prüfen ob schnelles Messen aktiv ist und ob dies wieder auf Standard zurück gesetzt werden muss
        if messhandler.schnelles_messen:
            if (now - messhandler.startzeit_schnelles_messen).total_seconds() > \
                    CONFIG["mess_cfg"]["dauer_schnelles_messintervall"]:
                messhandler.off_schnelles_messintervall()

        if (now - start_messzeitpunkt).total_seconds() > messhandler.pausenzeit:

            # Prüfe welche Messwerte auszulesen sind
            messauftrag = messhandler.erstelle_auszulesende_messregister()

            # Messauftrag abarbeiten und Zeitpunk ergänzen
            if messauftrag:
                start_messzeitpunkt = datetime.datetime.now()
                messwerte = smartmeter.read_input_values(messauftrag)
                LOGGER.debug("Messdauer: {}".format(datetime.datetime.now() - start_messzeitpunkt))
                messwerte["ts"] = now
                messhandler.add_messwerte(messwerte)

            if not messhandler.schnelles_messen:
                messhandler.reduziere_durchlauf_anzahl()
                messhandler.durchlauf_zuruecksetzen(messauftrag)
                if telegram_bot is not None:
                    telegram_bot.get_updates()

            # Schreibe die Messdaten in die Datenbank nach eingestellten Intervall
            if (now - zeitpunkt_daten_gesendet).total_seconds() > messhandler.intervall_daten_senden:
                start_schreiben = datetime.datetime.now()
                messhandler.schreibe_messwerte(datenbankschnittstelle)
                LOGGER.debug("DB Dauer schreiben: {}".format(datetime.datetime.now() - start_schreiben))
                zeitpunkt_daten_gesendet = now
            LOGGER.debug("Durchlaufdauer: {}".format(datetime.datetime.now() - now))
        time.sleep(0.2)


if __name__ == "__main__":
    nofailure = False
    try:
        main()
    finally:
        if not nofailure:
            fehlermeldung_schreiben(traceback.format_exc())
            LOGGER.exception("Schwerwiegender Fehler aufgetreten")
