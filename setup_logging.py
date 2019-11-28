#!/usr/bin/python3
"""
Beschreibung:
Hilfskript zum Erstellen einer logging Instanz in Abhängigkeit, ob das Skript manuell gestartet worden ist oder
ob das Skript per Service Unit gestartet wurde
Abhängig dessen wird entweder die Logging Instanz mit einem JournalHandler erstellt (Service Unit)
oder mit einem StreamHandler (manuell)

Author: Hofei
Datum: 03.08.2018
Version: 0.1
"""
import logging
import os
import shlex
import subprocess

from systemd import journal


def __setup_logging(loglevel, frm, startmethode, unitname):
    """
    Erstellt die Logger Instanz für das Skript
    """
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    logger.handlers = []
    if startmethode == "auto":
        log_handler = journal.JournalHandler(SYSLOG_IDENTIFIER=unitname)

    else:
        log_handler = logging.StreamHandler()
    log_handler.setLevel(loglevel)
    log_handler.setFormatter(frm)
    logger.addHandler(log_handler)
    return logger


def __get_service_unit_pid(unitname):
    """Ermittelt ob  das ausführende Skript mit einer Service Unit gestartet worden ist, wenn ja so ist das
    Ergebnis (pid_service_unit) != 0"""
    cmd = "systemctl show -p MainPID {}".format(unitname)
    cmd = shlex.split(cmd)
    antwort = subprocess.run(cmd, stdout=subprocess.PIPE)
    ausgabe = antwort.stdout
    # strip entfernt \n, split teilt am = in eine Liste und [1] weißt die Zahl in die Variable zu
    pid_service_unit = int(ausgabe.decode().strip().split("=")[1])
    return pid_service_unit


def __get_startmethode(unitname):
    """Verglicht die PID vom skript mit der pid Service Unit Prüfung
    wenn die Nummern gleich sind wird auf auto gestellt, wenn nicht auf manuell"""
    pid_service_unit = __get_service_unit_pid(unitname)
    pid_skript = os.getpid()
    if pid_service_unit == pid_skript:
        startmethode = "auto"
    else:
        startmethode = "manuell"
    return startmethode


def __set_loggerformat(startmethode):
    """Stellt die passende Formattierung ein"""
    if startmethode == "auto":
        frm = logging.Formatter("%(levelname)s: %(message)s", "%d.%m.%Y %H:%M:%S")
    else:
        frm = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%d.%m.%Y %H:%M:%S")
    return frm


def create_logger(unitname, loglevel):
    """Dies ist die aufzurufende Funktion bei der Verwendung des Moduls von außen
    Liefert die fertige Logging Instanz zurück"""
    startmethode = __get_startmethode(unitname)
    frm = __set_loggerformat(startmethode)
    return __setup_logging(loglevel, frm, startmethode, unitname)


if __name__ == "__main__":
    logger = create_logger("testunit", 10)
    logger.debug("Testnachricht")
