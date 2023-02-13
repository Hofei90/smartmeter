# Smartmeter

## Ziel des Projektes:

Stromzähler/Smartmeter via ModBus und Raspberry Pi auslesen, die Werte in einer Datenbank speichern und mit Grafana visualisieren

# Vorbereitungen

## Benötigte Hardware

* Verwendeter Stromzähler: 
SDM530 von bg-etech

Ebenso möglich ist der Typ DDS353B, [SDM230](https://stromzähler.eu/stromzaehler/wechselstromzaehler/fuer-hutschiene-geeicht/216/sdm230modbus-mid-1phasen-2te-lcd-wechselstromzaehler?number=1121216-M22), [SDM630](https://stromzähler.eu/stromzaehler/drehstromzaehler/fuer-hutschiene-geeicht/120/sdm630modbus-v2-mid-zweirichtungs-multifunktionsstromzaehler-mit-rs485-und-2x-s0?number=1141213-M22) (hier Danke für die Integration an 
[rpi-joe](https://forum-raspberrypi.de/user/5786-rpi-joe/) aus dem deutschen Raspberry Pi Forum)
* Raspberry Pi mit Zubehör
* USB ModBus Adapter: z.B. [hier](https://www.ebay.de/itm/255283310832)
  
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
* minimalmodbus

Installation dieser:

Apt Installation erfordert ggf. root Rechte! Paketquellen zuvor updaten. (apt update)

```console
apt install build-essential libssl-dev libffi-dev python3-dev libpq5 git
git clone https://github.com/Hofei90/smartmeter.git /home/pi/smartmeter
cd /home/pi/smartmeter
pip3 install --user -r requirements.txt
git submodule init && git submodule update
```

Wird als Datenbank **mysql/mariadb** verwendet, so muss noch folgendes Paket installiert werden
```console
pip3 install --user PyMySQL
```

Wird als Datenbank **PostgreSQL**, so muss noch folgendes Paket installiert werden
```console
pip3 install --user psycopg2
```

Für **sqlite3** ist keine weitere Installation notwendig.


### Telegram (Optional)
Ist der Telegrambot nicht erwünscht, so muss in der Konfigurationsdatei `false` eingetragen werden.
Aktuell ist es nur möglich, mit dem Bot das Messintervall zu verkürzen.


### MQTT (Optional)
Wird eine Datenübertragung an MQTT gewünscht, so muss in der Konfigurationsdatei is_active auf `true` gesetzt werden
und die Konfiguration für MQTT ausgefüllt werden.

## Programm einrichten

### Konfiguration anpassen

```console
cp smartmeter_cfg_vorlage.toml smartmeter_cfg.toml
```

Anschließend die `smartmeter_cfg.toml` anpassen.
Konfigurationsdatei muss im selben Ordner wie die Skripte mit dem Namen `smartmeter_cfg.toml` gespeichert werden
Bei der Anpassung sind `< >` zu entfernen - `" "` müssen stehen bleiben.


## Inbetriebnahme

### Erstmaliger Test:

`python3 smartmeter.py` ausführen

Wenn dieser Erfolgreich verläuft, erhält man folgende Meldung

```jsunicoderegexp
18.03.2021 10:27:45 INFO: Durchlaufintervall in Config aktualisiert
 Programm wird beendet. Bitte neu starten
```
Bevor nun das Programm neu gestartet wird, nochmals die Konfigurationsdatei öffnen und die Einträge bei 
Durchlaufintervall prüfen und den eigenen Wünschen anpassen.
Soll ein Parameter nie gemessen werden, so ist der Wert auf `false` zu stellen.
Ansonsten angeben, bei dem wievielten Durchlauf der entsprechenden Wert jeweils ausgelesen und gespeichert werden soll.

Nun das Programm erneut starten, erscheint anschließend keine Fehlermeldung, so kann eine Service Unit für den Autostart 
erstellt werden.

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
