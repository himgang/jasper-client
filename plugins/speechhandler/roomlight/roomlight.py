# -*- coding: utf-8 -*-
import datetime
import paho.mqtt.client as paho
from jasper import app_utils
from jasper import plugin
# make this configurable
broker="192.168.1.199"
port=1883
topic="himanshuroom"
message="light2"

class Roomlight(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [self.gettext("ROOM LIGHT"),self.gettext("ROOMLIGHT")]

    def handle(self, text, mic):
        """
        sends a message to mosquitto server to change current state of fan.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        pub = paho.Client()
        pub.connect(broker,port)
        pub.publish(topic,message) 
        fmt = "changing state of roomlight"
        mic.say(self.gettext(fmt).format(fmt))

    def is_valid(self, text):
        """
        Returns True if input is related to the time.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
