# Smartmeter

## Ziel des Projektes

Stromzähler/Smartmeter via ModBus und Raspberry Pi auslesen, die Werte in eine Datenbank speichern und mit Grafana visualisieren.

## Übersicht

* `EletricMeter.py`: enthält die Klassen für die Stromzähler
* `smartmeter.py`: Ausführbares Skript (Hauptskript)
* `smartmeter_telegrambot.py`: Enthält den Telegrambot
* `telegram_bot_api.py`: API für den Telegrambot

## Vorbereitungen

### Benötigte Hardware

* Verwendeter Stromzähler: [SDM530 von bg-etech](http://bg-etech.de/bgshop/product_info.php/drehstromzaehler-sdm530-modbus-p-461)
* Ebenso möglich ist der Typ SDM230 (hier wurde aber die Klasse in der Software noch nicht geprüft) oder ähnliche Stromzähler mit ModBus Schnittstelle
Raspberry Pi mit Zubehör
* USB ModBus Adapter: z.B hier
Gibts auch billiger, aber da war mir die Wartezeit im Verhältnis zum Preis zu hoch
geschirmtes Buskabel lt. Anleitung vom Stromzähler
* 2x 120Ohm 1/4Watt Abschlusswiderstand

**Einbau des Stromzählers nur durch Elektrofachpersonal!
Angaben ohne Gewähr! Besser nochmals nach Anleitung prüfen**

### Benötigte Software

* Python 3.5 oder höher
* PostgreSQL (optional mit timescale)
* Andere Datenbanken wären auch möglich, hierfür existiert aber noch keine Schnittstelle
* Grafana zur Visualisierung

#### Benötigte Python Module

* Toml
* SQLAlchemy
* sshtunnel
* serial
* minimalmodbus in Version 0.7 (neuer funktioniert nicht!)

Installation dieser:

Apt Installation erfordert ggf. root Rechte! Paketquellen zuvor updaten. (apt update)

```console
apt install build-essential libssl-dev libffi-dev python3-dev libpq5
pip3 install --user -r requirements.txt
```

#### Telegram

Telegrambot bei Botfather registrieren.

Wenn die Verwendung des Telegrambots nicht erwünscht ist müssen die entsprechenden Zeilen im Hauptskript
auskommentiert werden.

#### Datenbank vorbereiten

Tabellenspalten müssen den Namen der Messwerte besitzen.

```sql
-- Table: public.smartmeter

-- DROP TABLE public.smartmeter;

CREATE TABLE public.smartmeter (
    ts timestamp with time zone NOT NULL,
    ah_seit_reset double precision,
    aktuelle_gesamtblindleistung double precision,
    aktuelle_gesamtscheinleistung double precision,
    aktuelle_gesamtwirkleistung double precision,
    aktueller_gesamtleistungsfaktor double precision,
    aktueller_gesamtphasenwinkel double precision,
    aktueller_gesamtstrom double precision,
    blindleistung_l1 double precision,
    blindleistung_l2 double precision,
    blindleistung_l3 double precision,
    durchschnittliche_spannung_zu_n double precision,
    durchschnittlicher_strom_zu_n double precision,
    durchschnittsspannung_l_l double precision,
    export_varh_seit_reset double precision,
    export_wh_seit_reset double precision,
    frequenz double precision,
    gesamtscheinleistung double precision,
    gesamtstrom_neutralleiter double precision,
    gesamtsystemleistungsfaktor double precision,
    gesamtwirkleistung double precision,
    import_varh_seit_reset double precision,
    import_wh_seit_reset double precision,
    leistungsfaktor_l1 double precision,
    leistungsfaktor_l2 double precision,
    leistungsfaktor_l3 double precision,
    max_gesamtscheinleistung double precision,
    max_gesamtwirkleistung double precision,
    max_strom_l1_demand double precision,
    max_strom_l2_demand double precision,
    max_strom_l3_demand double precision,
    max_strom_neutralleiter double precision,
    phasenwinkel_l1 double precision,
    phasenwinkel_l2 double precision,
    phasenwinkel_l3 double precision,
    scheinleistung_l1 double precision,
    scheinleistung_l2 double precision,
    scheinleistung_l3 double precision,
    spannung_l1 double precision,
    spannung_l1_l2 double precision,
    spannung_l2 double precision,
    spannung_l2_l3 double precision,
    spannung_l3 double precision,
    spannung_l3_l1 double precision,
    strom_l1 double precision,
    strom_l1_demand double precision,
    strom_l2 double precision,
    strom_l2_demand double precision,
    strom_l3 double precision,
    strom_l3_demand double precision,
    strom_neutralleiter double precision,
    thd_durchschnittliche_spannung_zu_l_l double precision,
    thd_durchschnittliche_spannung_zu_n double precision,
    thd_durchschnittlicher_strom_zu_n double precision,
    thd_spannung_l1 double precision,
    thd_spannung_l1_l2 double precision,
    thd_spannung_l2 double precision,
    thd_spannung_l2_l3 double precision,
    thd_spannung_l3 double precision,
    thd_spannung_l3_l1 double precision,
    thd_strom_l1 double precision,
    thd_strom_l2 double precision,
    thd_strom_l3 double precision,
    total_kvarh double precision,
    total_kwh double precision,
    vah_seit_reset double precision,
    wirkleistung_l1 double precision,
    wirkleistung_l2 double precision,
    wirkleistung_l3 double precision,
    CONSTRAINT smartmeter_pkey PRIMARY KEY (ts)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.smartmeter
OWNER to hofei;
```

Owner letzte Zeile entsprechend anpassen.

### Konfiguration anpassen

Konfigurationsdatei muss im selben Verzeichnis wie die Skripte mit dem Namen `smartmeter_cfg.toml` gespeichert werden.

```toml
[modbus]
serial_if="/dev/ttyUSB0"
serial_if_baud=19200
serial_if_byte=8
serial_if_par="E"
serial_if_stop=1
slave_addr=1

[pg]
ip = "datenbank.ip"
pguser = "datenbank user"
pgpw = "datenbank pw"
pgport = portnr
db = "datenbankname"
pfad_zu_ssh_auth = "/pfad/zu/ssh_auth.toml"
intervall_daten_senden = 300
dauer_schnellintervall = 120
schnellintervall = 4

[telegram_bot]
token = "telegramtoken"

# Zeit in Sekunden, Was nicht aufgeführt ist, wird nicht ausgelesen
[[messintervall]]
Spannung_L1= 10
Spannung_L2= 10
Spannung_L3= 10
Strom_L1= 5
Strom_L2= 5
Strom_L3= 5
Wirkleistung_L1= 10
Wirkleistung_L2= 10
Wirkleistung_L3= 10
Scheinleistung_L1= 10
Scheinleistung_L2= 10
Scheinleistung_L3= 10
Blindleistung_L1= 10
Blindleistung_L2= 10
Blindleistung_L3= 10
Leistungsfaktor_L1= 10
Leistungsfaktor_L2= 10
Leistungsfaktor_L3= 10
Phasenwinkel_L1= 10
Phasenwinkel_L2= 10
Phasenwinkel_L3= 10
Durchschnittliche_Spannung_zu_N= 300
Durchschnittlicher_Strom_zu_N= 300
aktueller_Gesamtstrom= 10
aktuelle_Gesamtwirkleistung= 10
aktuelle_Gesamtscheinleistung= 10
aktuelle_Gesamtblindleistung= 10
aktueller_Gesamtleistungsfaktor= 10
aktueller_Gesamtphasenwinkel= 10
Frequenz= 10
Import_Wh_seit_reset= 300
Export_Wh_seit_reset= 300
Import_VArh_seit_reset= 300
Export_VArh_seit_reset= 300
VAh_seit_reset= 300
Ah_seit_reset= 300
Gesamtwirkleistung= 999999
Max_Gesamtwirkleistung= 300
Gesamtscheinleistung= 999999
Max_Gesamtscheinleistung= 300
Gesamtstrom_Neutralleiter= 999999
Max_Strom_Neutralleiter= 300
Spannung_L1_L2= 10
Spannung_L2_L3= 10
Spannung_L3_L1= 10
Durchschnittsspannung_L_L= 10
Strom_Neutralleiter= 10
THD_Spannung_L1= 10
THD_Spannung_L2= 10
THD_Spannung_L3= 10
THD_Strom_L1= 10
THD_Strom_L2= 10
THD_Strom_L3= 10
THD_Durchschnittliche_Spannung_zu_N= 10
THD_Durchschnittlicher_Strom_zu_N= 10
Gesamtsystemleistungsfaktor= 10
Strom_L1_demand= 999999
Strom_L2_demand= 999999
Strom_L3_demand= 999999
Max_Strom_L1_demand= 999999
Max_Strom_L2_demand= 999999
Max_Strom_L3_demand= 999999
THD_Spannung_L1_L2= 10
THD_Spannung_L2_L3= 10
THD_Spannung_L3_L1= 10
THD_Durchschnittliche_Spannung_zu_L_L= 10
Total_kwh= 300
Total_kvarh= 300
```

## Inbetriebnahme

### Erstmaliger Test

```console
python3 smartmeter.py
```

Wenn dies erfolgreich verläuft, mit dem folgenden Abschnitt fortfahren.

### Service Unit erstellen

_Alle folgenden Befehle erfordern Root-Rechte._

`/etc/systemd/system/smartmeter.service` mit folgendem Inhalt erstellen:

```systemd
# Pfad zum speichern: /etc/systemd/system/smartmeter.service
[Unit]
Description=ServiceUnit zum starten des Smartmeters
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/smartmeter/smartmeter.py
User=pi


[Install]
WantedBy=multi-user.target
```

Systemd-Unit starten:

```console
systemctl start smartmeter.service
```

Kontrolle ob Skript nun wieder aktiv ist, wenn ja automtische Ausführung anlegen:

```console
systemctl enable smartmeter.service
```

## Grafana

Die Visualisierung findet in Grafana statt, auf nähere Ausführungen wird hier jedoch verzichtet, natürlich können die
Messwerte mit anderen Tools visualsiert werden.
