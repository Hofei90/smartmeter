import datetime
from dataclasses import dataclass

import requests
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Smartmeter:
    ts = datetime.datetime
    Spannung_L1: float
    Spannung_L2: float
    Spannung_L3: float
    Strom_L1: float
    Strom_L2: float
    Strom_L3: float
    Wirkleistung_L1: float
    Wirkleistung_L2: float
    Wirkleistung_L3: float
    Scheinleistung_L1: float
    Scheinleistung_L2: float
    Scheinleistung_L3: float
    Blindleistung_L1: float
    Blindleistung_L2: float
    Blindleistung_L3: float
    Leistungsfaktor_L1: float
    Leistungsfaktor_L2: float
    Leistungsfaktor_L3: float
    Phasenwinkel_L1: float
    Phasenwinkel_L2: float
    Phasenwinkel_L3: float
    Durchschnittliche_Spannung_zu_N: float
    Durchschnittlicher_Strom_zu_N: float
    aktueller_Gesamtstrom: float
    aktuelle_Gesamtwirkleistung: float
    aktuelle_Gesamtscheinleistung: float
    aktuelle_Gesamtblindleistung: float
    aktueller_Gesamtleistungsfaktor: float
    aktueller_Gesamtphasenwinkel: float
    Frequenz: float
    Import_Wh_seit_reset: float
    Export_Wh_seit_reset: float
    Import_VArh_seit_reset: float
    Export_VArh_seit_reset: float
    VAh_seit_reset: float
    Ah_seit_reset: float
    Gesamtwirkleistung: float
    Max_Gesamtwirkleistung: float
    Gesamtscheinleistung: float
    Max_Gesamtscheinleistung: float
    Gesamtstrom_Neutralleiter: float
    Max_Strom_Neutralleiter: float
    Spannung_L1_L2: float
    Spannung_L2_L3: float
    Spannung_L3_L1: float
    Durchschnittsspannung_L_L: float
    Strom_Neutralleiter: float
    THD_Spannung_L1: float
    THD_Spannung_L2: float
    THD_Spannung_L3: float
    THD_Strom_L1: float
    THD_Strom_L2: float
    THD_Strom_L3: float
    THD_Durchschnittliche_Spannung_zu_N: float
    THD_Durchschnittlicher_Strom_zu_N: float
    Gesamtsystemleistungsfaktor: float
    Strom_L1_demand: float
    Strom_L2_demand: float
    Strom_L3_demand: float
    Max_Strom_L1_demand: float
    Max_Strom_L2_demand: float
    Max_Strom_L3_demand: float
    THD_Spannung_L1_L2: float
    THD_Spannung_L2_L3: float
    THD_Spannung_L3_L1: float
    THD_Durchschnittliche_Spannung_zu_L_L: float
    Total_kwh: float
    Total_kvarh: float


def sende_daten(url, headers, data):
    return requests.post(url, headers=headers, data=data)
