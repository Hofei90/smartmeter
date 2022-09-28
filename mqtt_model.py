import paho.mqtt.publish as publish

class MQTTModel:
    #Setting default values
    configBroker = "127.0.0.1"
    configPort = "1883"
    configUsername = ""
    configPassword = ""
    configTopic = "/smartmeter/"

    #Initialise the MQTT data, aka. overwriting the default values with config file values
    def __init__(self, broker, port, topic, username, password):
        self.configBroker = broker
        self.configPort = port
        self.configUsername = username
        self.configPassword = password
        
        if topic:
            self.configTopic = topic

    #we send the measured values as 
    # <topic><key> <value>
    def send(self, daten, logger):
        #prepare messages to MQTT

        msgs = []
        for i, (k, v) in enumerate(daten[0].items()):
            #we don't need a time stamp as the data is from now
            if k != "ts":
                msgs.append({'topic': self.configTopic + k, 'payload': str(v)})
        
        #send data to MQTT with a single call as it handles connects and disconnects itself
        if self.configUsername != "":
            authData = {'username':self.configUsername, 'password':self.configPassword}
            publish.multiple(msgs, hostname=self.configBroker, port=int(self.configPort), client_id="smartmeter", keepalive=60, auth=authData)
        else:
            publish.multiple(msgs, hostname=self.configBroker, port=int(self.configPort), client_id="smartmeter", keepalive=60)
