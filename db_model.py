import peewee

DB_PROXY = peewee.Proxy()


class BaseModel(peewee.Model):
    class Meta:
        database = DB_PROXY


class DDS353B(BaseModel):
    ts = peewee.DateTimeField(primary_key=True)
    power = peewee.FloatField(null=True)


class SDM72DM(BaseModel):
    ts = peewee.DateTimeField(primary_key=True)
    aktuelle_gesamtwirkleistung = peewee.FloatField(null=True)
    import_wh_seit_reset = peewee.FloatField(null=True)
    export_wh_seit_reset = peewee.FloatField(null=True)
    total_kwh = peewee.FloatField(null=True)
    settable_total_kwh = peewee.FloatField(null=True)
    settable_import_kwh = peewee.FloatField(null=True)
    setabble_export_kwh = peewee.FloatField(null=True)
    import_power = peewee.FloatField(null=True)
    export_power = peewee.FloatField(null=True)


class SDM230(BaseModel):
    ts = peewee.DateTimeField(primary_key=True)
    spannung_l1 = peewee.FloatField(null=True)
    strom_l1 = peewee.FloatField(null=True)
    wirkleistung_l1 = peewee.FloatField(null=True)
    scheinleistung_l1 = peewee.FloatField(null=True)
    blindleistung_l1 = peewee.FloatField(null=True)
    leistungsfaktor_l1 = peewee.FloatField(null=True)
    phasenwinkel_l1 = peewee.FloatField(null=True)
    frequenz = peewee.FloatField(null=True)
    import_wh_seit_reset = peewee.FloatField(null=True)
    export_wh_seit_reset = peewee.FloatField(null=True)
    import_varh_seit_reset = peewee.FloatField(null=True)
    export_varh_seit_reset = peewee.FloatField(null=True)
    gesamtwirkleistung = peewee.FloatField(null=True)
    max_gesamtwirkleistung = peewee.FloatField(null=True)
    currentsystempositivepowerdemand = peewee.FloatField(null=True)
    maximumsystempositivepowerdemand = peewee.FloatField(null=True)
    currentsystemreversepowerdemand = peewee.FloatField(null=True)
    strom_l1_demand = peewee.FloatField(null=True)
    max_strom_l1_demand = peewee.FloatField(null=True)
    total_kwh = peewee.FloatField(null=True)
    total_kvarh = peewee.FloatField(null=True)


class SDM530(BaseModel):
    ts = peewee.DateTimeField(primary_key=True)
    ah_seit_reset = peewee.FloatField(null=True)
    aktuelle_gesamtblindleistung = peewee.FloatField(null=True)
    aktuelle_gesamtscheinleistung = peewee.FloatField(null=True)
    aktuelle_gesamtwirkleistung = peewee.FloatField(null=True)
    aktueller_gesamtleistungsfaktor = peewee.FloatField(null=True)
    aktueller_gesamtphasenwinkel = peewee.FloatField(null=True)
    aktueller_gesamtstrom = peewee.FloatField(null=True)
    blindleistung_l1 = peewee.FloatField(null=True)
    blindleistung_l2 = peewee.FloatField(null=True)
    blindleistung_l3 = peewee.FloatField(null=True)
    durchschnittliche_spannung_zu_n = peewee.FloatField(null=True)
    durchschnittlicher_strom_zu_n = peewee.FloatField(null=True)
    durchschnittsspannung_l_l = peewee.FloatField(null=True)
    export_varh_seit_reset = peewee.FloatField(null=True)
    export_wh_seit_reset = peewee.FloatField(null=True)
    frequenz = peewee.FloatField(null=True)
    gesamtscheinleistung = peewee.FloatField(null=True)
    gesamtstrom_neutralleiter = peewee.FloatField(null=True)
    gesamtsystemleistungsfaktor = peewee.FloatField(null=True)
    gesamtwirkleistung = peewee.FloatField(null=True)
    import_varh_seit_reset = peewee.FloatField(null=True)
    import_wh_seit_reset = peewee.FloatField(null=True)
    leistungsfaktor_l1 = peewee.FloatField(null=True)
    leistungsfaktor_l2 = peewee.FloatField(null=True)
    leistungsfaktor_l3 = peewee.FloatField(null=True)
    max_gesamtscheinleistung = peewee.FloatField(null=True)
    max_gesamtwirkleistung = peewee.FloatField(null=True)
    max_strom_l1_demand = peewee.FloatField(null=True)
    max_strom_l2_demand = peewee.FloatField(null=True)
    max_strom_l3_demand = peewee.FloatField(null=True)
    max_strom_neutralleiter = peewee.FloatField(null=True)
    phasenwinkel_l1 = peewee.FloatField(null=True)
    phasenwinkel_l2 = peewee.FloatField(null=True)
    phasenwinkel_l3 = peewee.FloatField(null=True)
    scheinleistung_l1 = peewee.FloatField(null=True)
    scheinleistung_l2 = peewee.FloatField(null=True)
    scheinleistung_l3 = peewee.FloatField(null=True)
    spannung_l1 = peewee.FloatField(null=True)
    spannung_l1_l2 = peewee.FloatField(null=True)
    spannung_l2 = peewee.FloatField(null=True)
    spannung_l2_l3 = peewee.FloatField(null=True)
    spannung_l3 = peewee.FloatField(null=True)
    spannung_l3_l1 = peewee.FloatField(null=True)
    strom_l1 = peewee.FloatField(null=True)
    strom_l1_demand = peewee.FloatField(null=True)
    strom_l2 = peewee.FloatField(null=True)
    strom_l2_demand = peewee.FloatField(null=True)
    strom_l3 = peewee.FloatField(null=True)
    strom_l3_demand = peewee.FloatField(null=True)
    strom_neutralleiter = peewee.FloatField(null=True)
    thd_durchschnittliche_spannung_zu_l_l = peewee.FloatField(null=True)
    thd_durchschnittliche_spannung_zu_n = peewee.FloatField(null=True)
    thd_durchschnittlicher_strom_zu_n = peewee.FloatField(null=True)
    thd_spannung_l1 = peewee.FloatField(null=True)
    thd_spannung_l1_l2 = peewee.FloatField(null=True)
    thd_spannung_l2 = peewee.FloatField(null=True)
    thd_spannung_l2_l3 = peewee.FloatField(null=True)
    thd_spannung_l3 = peewee.FloatField(null=True)
    thd_spannung_l3_l1 = peewee.FloatField(null=True)
    thd_strom_l1 = peewee.FloatField(null=True)
    thd_strom_l2 = peewee.FloatField(null=True)
    thd_strom_l3 = peewee.FloatField(null=True)
    total_kvarh = peewee.FloatField(null=True)
    total_kwh = peewee.FloatField(null=True)
    vah_seit_reset = peewee.FloatField(null=True)
    wirkleistung_l1 = peewee.FloatField(null=True)
    wirkleistung_l2 = peewee.FloatField(null=True)
    wirkleistung_l3 = peewee.FloatField(null=True)


class SDM630(BaseModel):
    ts = peewee.DateTimeField(primary_key=True)
    spannung_l1 = peewee.FloatField(null=True)
    spannung_l2 = peewee.FloatField(null=True)
    spannung_l3 = peewee.FloatField(null=True)
    strom_l1 = peewee.FloatField(null=True)
    strom_l2 = peewee.FloatField(null=True)
    strom_l3 = peewee.FloatField(null=True)
    wirkleistung_l1 = peewee.FloatField(null=True)
    wirkleistung_l2 = peewee.FloatField(null=True)
    wirkleistung_l3 = peewee.FloatField(null=True)
    scheinleistung_l1 = peewee.FloatField(null=True)
    scheinleistung_l2 = peewee.FloatField(null=True)
    scheinleistung_l3 = peewee.FloatField(null=True)
    blindleistung_l1 = peewee.FloatField(null=True)
    blindleistung_l2 = peewee.FloatField(null=True)
    blindleistung_l3 = peewee.FloatField(null=True)
    leistungsfaktor_l1 = peewee.FloatField(null=True)
    leistungsfaktor_l2 = peewee.FloatField(null=True)
    leistungsfaktor_l3 = peewee.FloatField(null=True)
    phasenwinkel_l1 = peewee.FloatField(null=True)
    phasenwinkel_l2 = peewee.FloatField(null=True)
    phasenwinkel_l3 = peewee.FloatField(null=True)
    durchschnittliche_spannung_zu_n = peewee.FloatField(null=True)
    durchschnittlicher_strom_zu_n = peewee.FloatField(null=True)
    aktueller_gesamtstrom = peewee.FloatField(null=True)
    aktuelle_gesamtwirkleistung = peewee.FloatField(null=True)
    aktuelle_gesamtscheinleistung = peewee.FloatField(null=True)
    aktuelle_gesamtblindleistung = peewee.FloatField(null=True)
    aktueller_gesamtleistungsfaktor = peewee.FloatField(null=True)
    aktueller_gesamtphasenwinkel = peewee.FloatField(null=True)
    frequenz = peewee.FloatField(null=True)
    import_wh_seit_reset = peewee.FloatField(null=True)
    export_wh_seit_reset = peewee.FloatField(null=True)
    import_varh_seit_reset = peewee.FloatField(null=True)
    export_varh_seit_reset = peewee.FloatField(null=True)
    vah_seit_reset = peewee.FloatField(null=True)
    ah_seit_reset = peewee.FloatField(null=True)
    gesamtwirkleistung = peewee.FloatField(null=True)
    max_gesamtwirkleistung = peewee.FloatField(null=True)
    gesamtscheinleistung = peewee.FloatField(null=True)
    max_gesamtscheinleistung = peewee.FloatField(null=True)
    gesamtstrom_neutralleiter = peewee.FloatField(null=True)
    max_strom_neutralleiter = peewee.FloatField(null=True)
    spannung_l1_l2 = peewee.FloatField(null=True)
    spannung_l2_l3 = peewee.FloatField(null=True)
    spannung_l3_l1 = peewee.FloatField(null=True)
    durchschnittsspannung_l_l = peewee.FloatField(null=True)
    strom_neutralleiter = peewee.FloatField(null=True)
    thd_spannung_l1 = peewee.FloatField(null=True)
    thd_spannung_l2 = peewee.FloatField(null=True)
    thd_spannung_l3 = peewee.FloatField(null=True)
    thd_strom_l1 = peewee.FloatField(null=True)
    thd_strom_l2 = peewee.FloatField(null=True)
    thd_strom_l3 = peewee.FloatField(null=True)
    thd_durchschnittliche_spannung_zu_n = peewee.FloatField(null=True)
    thd_durchschnittlicher_strom_zu_n = peewee.FloatField(null=True)
    strom_l1_demand = peewee.FloatField(null=True)
    strom_l2_demand = peewee.FloatField(null=True)
    strom_l3_demand = peewee.FloatField(null=True)
    max_strom_l1_demand = peewee.FloatField(null=True)
    max_strom_l2_demand = peewee.FloatField(null=True)
    max_strom_l3_demand = peewee.FloatField(null=True)
    thd_spannung_l1_l2 = peewee.FloatField(null=True)
    thd_spannung_l2_l3 = peewee.FloatField(null=True)
    thd_spannung_l3_l1 = peewee.FloatField(null=True)
    thd_durchschnittliche_spannung_zu_l_l = peewee.FloatField(null=True)
    total_kwh = peewee.FloatField(null=True)
    total_kvarh = peewee.FloatField(null=True)
    import_l1_kwh = peewee.FloatField(null=True)
    import_l2_kwh = peewee.FloatField(null=True)
    import_l3_kwh = peewee.FloatField(null=True)
    export_l1_kwh = peewee.FloatField(null=True)
    export_l2_kwh = peewee.FloatField(null=True)
    export_l3_kwh = peewee.FloatField(null=True)
    gesamtstrom_l1_kwh = peewee.FloatField(null=True)
    gesamtstrom_l2_kwh = peewee.FloatField(null=True)
    gesamtstrom_l3_kwh = peewee.FloatField(null=True)
    import_l1_kvarh = peewee.FloatField(null=True)
    import_l2_kvarh = peewee.FloatField(null=True)
    import_l3_kvarh = peewee.FloatField(null=True)
    export_l1_kvarh = peewee.FloatField(null=True)
    export_l2_kvarh = peewee.FloatField(null=True)
    export_l3_kvarh = peewee.FloatField(null=True)
    total_l1_kvarh = peewee.FloatField(null=True)
    total_l2_kvarh = peewee.FloatField(null=True)
    total_l3_kvarh = peewee.FloatField(null=True)


class WS100(BaseModel):
    ts = peewee.DateTimeField(primary_key=True)
    gesamtwirkleistung = peewee.FloatField(null=True)
    total_kwh = peewee.FloatField(null=True)


def get_smartmeter_table(device):
    if device == "DDS353B":
        return DDS353B
    elif device == "SDM72DM":
        return SDM72DM
    elif device == "SDM230":
        return SDM230
    elif device == "SDM530":
        return SDM530
    elif device == "SDM630":
        return SDM630
    elif device == "WS100":
        return WS100
    else:
        raise ValueError("Devicename falsch oder nicht unterstützt?")


def insert_many(daten, db_table):
    daten_konvertiert = []
    for datensatz in daten:
        datensatz_konvertiert = {}
        for key, value in datensatz.items():
            datensatz_konvertiert[key.lower()] = value
        daten_konvertiert.append(datensatz_konvertiert)
    db_table.insert_many(daten_konvertiert).execute()


def create_tables(tables):
    DB_PROXY.create_tables(tables)


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
