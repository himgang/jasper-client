# -*- coding: utf-8 -*-
import datetime
from jasper import app_utils
from jasper import plugin


class GoodMorning(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [self.gettext("Good Morning"), self.gettext("GoodMorning")]

    def handle(self, text, mic):
        """
        Reports the current time based on the user's timezone.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        
        tz = app_utils.get_timezone(self.profile)
        now = datetime.datetime.now(tz=tz)
        if now.minute == 0:
            fmt = "Good Morning sir , It is {t:%l} {t:%P} right now."
        else:
            fmt = "Good Morning sir, It is {t:%l}:{t.minute} {t:%P} right now."
        mic.say(self.gettext(fmt).format(t=now))

    def is_valid(self, text):
        """
        Returns True if input is related to the time.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
