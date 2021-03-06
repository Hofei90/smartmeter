# Smartmeter

## Ziel des Projektes:

Stromzähler/Smartmeter via ModBus und Raspberry Pi auslesen, die Werte in einer Datenbank speichern und mit Grafana visualisieren

# Vorbereitungen

## Benötigte Hardware

* Verwendeter Stromzähler: [
SDM530 von bg-etech](https://stromzähler.eu/stromzaehler/drehstromzaehler/fuer-hutschiene-ungeeicht/22/sdm530modbus-multifunktionsmessgeraet-fuer-din-hutschiene?c=93)
* Ebenso möglich ist der Typ SDM230 (hier wurde aber die Klasse in der Software noch nicht geprüft) 
oder ähnliche Stromzähler mit ModBus Schnittstelle
* Raspberry Pi mit Zubehör
* USB ModBus Adapter: z.B. [hier](https://www.ebay.de/itm/RS485-Konverter-Bus-Adapter-Seriell-USB-RS-485-Schnittstelle-Modbus-Raspberry-Pi/252784174363?ssPageName=STRK%3AMEBIDX%3AIT&_trksid=p2060353.m2749.l2649)
  
  Gibts auch billiger, aber da war mir die Wartezeit im Verhältnis zum Preis zu hoch
* geschirmtes Buskabel (lt. Anleitung vom Stromzähler)
* 2x 120Ohm 1/4Watt Abschlusswiderstand

**Einbau des Stromzählers nur durch Elektrofachpersonal!
Angaben ohne Gewähr! Besser nochmals nach Anleitung prüfen**

## Benötigte Software

* Python 3.7 oder höher
* Grafana zur Visualisierung

### Unterstützte Datenbanken
Direkte Verbindung zu
* sqlite3
* mySQL
* PostgreSQL (optional mit timescale)

Für PostgreSQL gibt es noch eine weitere Möglichkeit der Datenübertragung:
* [postgrest](https://postgrest.org/en/v6.0/)

Postgrest ermöglicht die Datenübertragung über eine Web-API (muss vom Server natürlich bereitgestellt werden)

### Benötigte Python Module

* Toml
* Peewee
* serial
* minimalmodbus in Version 0.7 (neuer funktioniert nicht!)

Installation dieser:

Apt Installation erfordert ggf. root Rechte! Paketquellen zuvor updaten. (apt update)

```console
apt install build-essential libssl-dev libffi-dev python3-dev libpq5 git
pip3 install --user -r requirements.txt
git clone https://github.com/Hofei90/smartmeter.git /home/pi/smartmeter
cd /home/pi/smartmeter
git submodule init && git submodule update
```

### Telegram (Optional)
Ist der Telegrambot nicht erwünscht, so muss in der Konfigurationsdatei `false` eingetragen werden.
Aktuell ist es nur möglich, mit dem Bot das Messintervall zu verkürzen.


## Programm einrichten

### Konfiguration anpassen

```console
cp smartmeter_cfg_vorlage.toml smartmeter_cfg.toml
```

Anschließend die `smartmeter_cfg.toml` anpassen.
Konfigurationsdatei muss im selben Ordner wie die Skripte mit dem Namen `smartmeter_cfg.toml` gespeichert werden


## Inbetriebnahme

### Erstmaliger Test:

`python3 smartmeter.py` ausführen

Wenn dieser Erfolgreich verläuft:


### Service Unit erstellen

Ausführung erfordert root Rechte

`nano /etc/systemd/system/smartmeter.service`

```code
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

`systemctl start smartmeter.service`

Kontrolle ob Skript nun wieder aktiv ist, wenn ja automatische Ausführung anlegen:

`systemctl enable smartmeter.service`

## Grafana

Die Visualisierung findet in Grafana statt, auf nähere Ausführungen wird hier jedoch verzichtet, natürlich können die
Messwerte auch mit anderen Tools visualsiert werden.
