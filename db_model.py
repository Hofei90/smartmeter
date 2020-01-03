import peewee

DB_PROXY = peewee.Proxy()


class BaseModel(peewee.Model):
    class Meta:
        database = DB_PROXY


class Smartmeter(BaseModel):
    ts = peewee.DateTimeField(primary_key=True)
    Spannung_L1 = peewee.FloatField(null=True)
    Spannung_L2 = peewee.FloatField(null=True)
    Spannung_L3 = peewee.FloatField(null=True)
    Strom_L1 = peewee.FloatField(null=True)
    Strom_L2 = peewee.FloatField(null=True)
    Strom_L3 = peewee.FloatField(null=True)
    Wirkleistung_L1 = peewee.FloatField(null=True)
    Wirkleistung_L2 = peewee.FloatField(null=True)
    Wirkleistung_L3 = peewee.FloatField(null=True)
    Scheinleistung_L1 = peewee.FloatField(null=True)
    Scheinleistung_L2 = peewee.FloatField(null=True)
    Scheinleistung_L3 = peewee.FloatField(null=True)
    Blindleistung_L1 = peewee.FloatField(null=True)
    Blindleistung_L2 = peewee.FloatField(null=True)
    Blindleistung_L3 = peewee.FloatField(null=True)
    Leistungsfaktor_L1 = peewee.FloatField(null=True)
    Leistungsfaktor_L2 = peewee.FloatField(null=True)
    Leistungsfaktor_L3 = peewee.FloatField(null=True)
    Phasenwinkel_L1 = peewee.FloatField(null=True)
    Phasenwinkel_L2 = peewee.FloatField(null=True)
    Phasenwinkel_L3 = peewee.FloatField(null=True)
    Durchschnittliche_Spannung_zu_N = peewee.FloatField(null=True)
    Durchschnittlicher_Strom_zu_N = peewee.FloatField(null=True)
    aktueller_Gesamtstrom = peewee.FloatField(null=True)
    aktuelle_Gesamtwirkleistung = peewee.FloatField(null=True)
    aktuelle_Gesamtscheinleistung = peewee.FloatField(null=True)
    aktuelle_Gesamtblindleistung = peewee.FloatField(null=True)
    aktueller_Gesamtleistungsfaktor = peewee.FloatField(null=True)
    aktueller_Gesamtphasenwinkel = peewee.FloatField(null=True)
    Frequenz = peewee.FloatField(null=True)
    Import_Wh_seit_reset = peewee.FloatField(null=True)
    Export_Wh_seit_reset = peewee.FloatField(null=True)
    Import_VArh_seit_reset = peewee.FloatField(null=True)
    Export_VArh_seit_reset = peewee.FloatField(null=True)
    VAh_seit_reset = peewee.FloatField(null=True)
    Ah_seit_reset = peewee.FloatField(null=True)
    Gesamtwirkleistung = peewee.FloatField(null=True)
    Max_Gesamtwirkleistung = peewee.FloatField(null=True)
    Gesamtscheinleistung = peewee.FloatField(null=True)
    Max_Gesamtscheinleistung = peewee.FloatField(null=True)
    Gesamtstrom_Neutralleiter = peewee.FloatField(null=True)
    Max_Strom_Neutralleiter = peewee.FloatField(null=True)
    Spannung_L1_L2 = peewee.FloatField(null=True)
    Spannung_L2_L3 = peewee.FloatField(null=True)
    Spannung_L3_L1 = peewee.FloatField(null=True)
    Durchschnittsspannung_L_L = peewee.FloatField(null=True)
    Strom_Neutralleiter = peewee.FloatField(null=True)
    THD_Spannung_L1 = peewee.FloatField(null=True)
    THD_Spannung_L2 = peewee.FloatField(null=True)
    THD_Spannung_L3 = peewee.FloatField(null=True)
    THD_Strom_L1 = peewee.FloatField(null=True)
    THD_Strom_L2 = peewee.FloatField(null=True)
    THD_Strom_L3 = peewee.FloatField(null=True)
    THD_Durchschnittliche_Spannung_zu_N = peewee.FloatField(null=True)
    THD_Durchschnittlicher_Strom_zu_N = peewee.FloatField(null=True)
    Gesamtsystemleistungsfaktor = peewee.FloatField(null=True)
    Strom_L1_demand = peewee.FloatField(null=True)
    Strom_L2_demand = peewee.FloatField(null=True)
    Strom_L3_demand = peewee.FloatField(null=True)
    Max_Strom_L1_demand = peewee.FloatField(null=True)
    Max_Strom_L2_demand = peewee.FloatField(null=True)
    Max_Strom_L3_demand = peewee.FloatField(null=True)
    THD_Spannung_L1_L2 = peewee.FloatField(null=True)
    THD_Spannung_L2_L3 = peewee.FloatField(null=True)
    THD_Spannung_L3_L1 = peewee.FloatField(null=True)
    THD_Durchschnittliche_Spannung_zu_L_L = peewee.FloatField(null=True)
    Total_kwh = peewee.FloatField(null=True)
    Total_kvarh = peewee.FloatField(null=True)


def init_db(name, type_="sqlite", config=None):
    config = config or {}
    drivers = {
        "sqlite": peewee.SqliteDatabase,
        "mysql": peewee.MySQLDatabase,
        "postgresql": peewee.PostgresqlDatabase,
    }

    try:
        cls = drivers[type_]
    except KeyError:
        raise ValueError("Unknown database type: {}".format(type_)) from None
    del config["database"]
    db = cls(name, **config)
    return db
