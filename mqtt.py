import paho.mqtt.publish as publish


class MQTT:
    # Wertinitialisierung von config
    def __init__(self, broker, port, topic, username, password):
        self.config_broker = broker
        self.config_port = port
        self.config_username = username
        self.config_password = password
        self.config_topic = topic

    # Wir schicken die daten als
    # <topic><key> <value>
    def send(self, daten, logger):
        # Vorbereitung der daten für MQTT
        msgs = []
        for i, (k, v) in enumerate(daten[0].items()):
            # wir brauchen keinen Zeitwert, weil alle Daten sind von jetzt
            if k != "ts":
                msgs.append({'topic': self.config_topic + k, 'payload': str(v)})
        
        # Data senden mit einem einzigen MQTT Aufruf
        if self.config_username != "":
            auth_data = {'username': self.config_username, 'password': self.config_password}
            publish.multiple(msgs, hostname=self.config_broker, port=int(self.config_port), client_id="smartmeter",
                             keepalive=60, auth=auth_data)
        else:
            publish.multiple(msgs, hostname=self.config_broker, port=int(self.config_port), client_id="smartmeter",
                             keepalive=60)
