import datetime
import json
from copy import deepcopy

import requests


def sende_daten(url, headers, daten, none_daten):
    for datensatz in daten:
        datensatz["ts"] = datensatz["ts"].strftime("%Y-%m-%d %H:%M:%S")
    daten_konvertiert = []
    for datensatz in daten:
        datensatz_konvertiert = deepcopy(none_daten)
        for key, value in datensatz.items():
            datensatz_konvertiert[key.lower()] = value
        daten_konvertiert.append(datensatz_konvertiert)

    json_daten = json.dumps(daten_konvertiert)
    print(json_daten)
    r = requests.post(url, headers=headers, data=json_daten)
    print(r.status_code)
    print(r.text)
