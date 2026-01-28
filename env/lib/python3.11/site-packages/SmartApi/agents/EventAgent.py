""" 
"""

import sys
import paho.mqtt.client as mqtt
from SmartAPI.agents.Agent import Agent
from SmartAPI.common.Tools import Tools
from threading import Thread

default_mqtt_broker_address = "broker.asema.com"
default_mqtt_broker_port    = 1883


class EventAgent(Agent):
    def __init__(self, callback, protocol = "mqtt", mqtt_topic = None, mqtt_broker_address = None, mqtt_broker_port = None):
        Agent.__init__(self)
        self.mqtt_topic = mqtt_topic
        if mqtt_broker_address is not None:
            self.mqtt_broker_address = mqtt_broker_address
        else:
            self.mqtt_broker_address = default_mqtt_broker_address
            
        if mqtt_broker_port is not None:
            self.mqtt_broker_port = mqtt_broker_port
        else:
             self.mqtt_broker_port = default_mqtt_broker_port
        
        self._cb = callback
        self.protocol = protocol
        self._th = None
        
    def connect(self):
        if self.protocol == "mqtt":
            self.mqtt_connect()
            
    # Callback for when the MQTT client connects.
    def on_mqtt_connect(self, client, userdata, flags, rc):
        client.subscribe(self.mqtt_topic)
    
    # Callback on broker socket disconnect
    def on_mqtt_disconnect(self, client, userdata, flags, rc):
        if rc != 0:
            print("Unexpected disconnection.")
        
    # Callback for when a notification is received.
    def on_mqtt_publish(self, client, userdata, msg):
        n = Tools.parseNotification(msg.payload)
        self._cb(n)
    
    def mqtt_connect(self):
        client = mqtt.Client()
        client.on_connect = self.on_mqtt_connect
        client.on_disconnect = self.on_mqtt_disconnect
        client.on_message = self.on_mqtt_publish
        
        client.connect(self.mqtt_broker_address, self.mqtt_broker_port, 60)
        
        # Wait for notifications
        self._th = Thread(target=client.loop_forever, )
        self._th.start()
