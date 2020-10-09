import datetime
import json
from copy import deepcopy

import requests


def sende_daten(url, headers, daten, none_daten, logger):
    for datensatz in daten:
        datensatz["ts"] = datensatz["ts"].strftime("%Y-%m-%d %H:%M:%S")
    daten_konvertiert = []
    for datensatz in daten:
        datensatz_konvertiert = deepcopy(none_daten)
        for key, value in datensatz.items():
            datensatz_konvertiert[key.lower()] = value
        daten_konvertiert.append(datensatz_konvertiert)

    json_daten = json.dumps(daten_konvertiert)
    logger.debug(json_daten)
    r = requests.post(url, headers=headers, data=json_daten)
    if r.status_code == 200 or r.status_code == 201:
        logger.debug(r.status_code)
        logger.debug(r.text)
    else:
        logger.error(r.status_code)
        logger.error(r.text)
