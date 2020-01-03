import datetime
from dataclasses import dataclass

import requests
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Smartmeter:
    ts = datetime.datetime
    Spannung_L1: float = None
    Spannung_L2: float = None
    Spannung_L3: float = None
    Strom_L1: float = None
    Strom_L2: float = None
    Strom_L3: float = None
    Wirkleistung_L1: float = None
    Wirkleistung_L2: float = None
    Wirkleistung_L3: float = None
    Scheinleistung_L1: float = None
    Scheinleistung_L2: float = None
    Scheinleistung_L3: float = None
    Blindleistung_L1: float = None
    Blindleistung_L2: float = None
    Blindleistung_L3: float = None
    Leistungsfaktor_L1: float = None
    Leistungsfaktor_L2: float = None
    Leistungsfaktor_L3: float = None
    Phasenwinkel_L1: float = None
    Phasenwinkel_L2: float = None
    Phasenwinkel_L3: float = None
    Durchschnittliche_Spannung_zu_N: float = None
    Durchschnittlicher_Strom_zu_N: float = None
    aktueller_Gesamtstrom: float = None
    aktuelle_Gesamtwirkleistung: float = None
    aktuelle_Gesamtscheinleistung: float = None
    aktuelle_Gesamtblindleistung: float = None
    aktueller_Gesamtleistungsfaktor: float = None
    aktueller_Gesamtphasenwinkel: float = None
    Frequenz: float = None
    Import_Wh_seit_reset: float = None
    Export_Wh_seit_reset: float = None
    Import_VArh_seit_reset: float = None
    Export_VArh_seit_reset: float = None
    VAh_seit_reset: float = None
    Ah_seit_reset: float = None
    Gesamtwirkleistung: float = None
    Max_Gesamtwirkleistung: float = None
    Gesamtscheinleistung: float = None
    Max_Gesamtscheinleistung: float = None
    Gesamtstrom_Neutralleiter: float = None
    Max_Strom_Neutralleiter: float = None
    Spannung_L1_L2: float = None
    Spannung_L2_L3: float = None
    Spannung_L3_L1: float = None
    Durchschnittsspannung_L_L: float = None
    Strom_Neutralleiter: float = None
    THD_Spannung_L1: float = None
    THD_Spannung_L2: float = None
    THD_Spannung_L3: float = None
    THD_Strom_L1: float = None
    THD_Strom_L2: float = None
    THD_Strom_L3: float = None
    THD_Durchschnittliche_Spannung_zu_N: float = None
    THD_Durchschnittlicher_Strom_zu_N: float = None
    Gesamtsystemleistungsfaktor: float = None
    Strom_L1_demand: float = None
    Strom_L2_demand: float = None
    Strom_L3_demand: float = None
    Max_Strom_L1_demand: float = None
    Max_Strom_L2_demand: float = None
    Max_Strom_L3_demand: float = None
    THD_Spannung_L1_L2: float = None
    THD_Spannung_L2_L3: float = None
    THD_Spannung_L3_L1: float = None
    THD_Durchschnittliche_Spannung_zu_L_L: float = None
    Total_kwh: float = None
    Total_kvarh: float = None


def sende_daten(url, headers, data):
    return requests.post(url, headers=headers, data=data)
