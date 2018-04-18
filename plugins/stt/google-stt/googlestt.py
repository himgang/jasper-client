import json
import logging
import urllib
import urlparse
import wave
import requests
import io
import os
import google
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from jasper import plugin



class GoogleSTTPlugin(plugin.STTPlugin):
    """
    Speech-To-Text implementation which relies on the Google Speech API.

    This implementation requires a Google API key to be present in profile.yml

    To obtain an API key:
    1. Join the Chromium Dev group:
       https://groups.google.com/a/chromium.org/forum/?fromgroups#!forum/chromium-dev
    2. Create a project through the Google Developers console:
       https://console.developers.google.com/project
    3. Select your project. In the sidebar, navigate to "APIs & Auth." Activate
       the Speech API.
    4. Under "APIs & Auth," navigate to "Credentials." Create a new key for
       public API access.
    5. Add your credentials to your profile.yml. Add an entry to the 'keys'
       section using the key name 'GOOGLE_SPEECH.' Sample configuration:
    6. Set the value of the 'stt_engine' key in your profile.yml to 'google'


    Excerpt from sample profile.yml:

        ...
        timezone: US/Pacific
        stt_engine: google
        keys:
            GOOGLE_SPEECH: $YOUR_KEY_HERE

    """

    def __init__(self, *args, **kwargs):
        plugin.STTPlugin.__init__(self, *args, **kwargs)
        # FIXME: get init args from config

        self._logger = logging.getLogger(__name__)
        self._request_url = None
        self._language = None
        self._api_key = None
        self._http = None
        try:
            language = self.profile['language']
        except KeyError:
            language = 'en-US'

        self.language = language.lower()
        self.api_key = self.profile['keys']['GOOGLE_SPEECH']

    @property
    def request_url(self):
        return self._request_url

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value
        self._regenerate_request_url()

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value
        self._regenerate_request_url()

    def _regenerate_request_url(self):
        if self.api_key and self.language:
            query = urllib.urlencode({'output': 'json',
                                      'client': 'chromium',
                                      'key': self.api_key,
                                      'lang': self.language,
                                      'maxresults': 6,
                                      'pfilter': 2})
            self._request_url = urlparse.urlunparse(
                ('https', 'www.google.com', '/speech-api/v2/recognize', '',
                 query, ''))
        else:
            self._request_url = None

    def transcribe(self, fp):
        """
        Performs STT via the Google Speech API, transcribing an audio file and
        returning an English string.

        Arguments:
        audio_file_path -- the path to the .wav file to be transcribed
        """

        if not self.api_key:
            self._logger.critical('API key missing, transcription request ' +
                                  'aborted.')
            return []
        elif not self.language:
            self._logger.critical('Language info missing, transcription ' +
                                  'request aborted.')
            return []

#         wav = io.open(fp, 'rb')
#         wav.close()
        with io.open(file_name, 'rb') as audio_file:
            data = audio_file.read()

        headers = {'content-type': 'audio/l16; rate=%s' % frame_rate}
        res = self.transcribett(data)
        results = [res,res]
#         r = self._http.post(self.request_url, data=data, headers=headers)
#         try:
#             r.raise_for_status()
#         except requests.exceptions.HTTPError:
#             self._logger.critical('Request failed with http status %d',
#                                   r.status_code)
#             if r.status_code == requests.codes['forbidden']:
#                 self._logger.warning('Status 403 is probably caused by an ' +
#                                      'invalid Google API key.')
#             return []
#         r.encoding = 'utf-8'
#         try:
#             # We cannot simply use r.json() because Google sends invalid json
#             # (i.e. multiple json objects, seperated by newlines. We only want
#             # the last one).
#             response = json.loads(list(r.text.strip().split('\n', 1))[-1])
#             if len(response['result']) == 0:
#                 # Response result is empty
#                 raise ValueError('Nothing has been transcribed.')
#             results = [alt['transcript'] for alt
#                        in response['result'][0]['alternative']]
#         except ValueError as e:
#             self._logger.warning('Empty response: %s', e.args[0])
#             results = []
#         except (KeyError, IndexError):
#             self._logger.warning('Cannot parse response.', exc_info=True)
#             results = []
#         else:
#             # Convert all results to uppercase
#             results = tuple(result.upper() for result in results)
#             self._logger.info('Transcribed: %r', results)
        return results
    
    def transcribett(self,data):

        # Instantiates a client
        client = speech.SpeechClient()

        # The name of the audio file to transcribe
        # Loads the audio into memory
        content = data
        audio = types.RecognitionAudio(content=content)

        config = types.RecognitionConfig(
            encoding=google.cloud.speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=48000,
            language_code='en-IN')

        # Detects speech in the audio file
        response = client.recognize(config, audio)
        self._logger.info('received response: %r',response)
        for result in response.results:
            self._logger.info('Transcribed: %r',result.alternatives[0].transcript)
        
        return response.results.alternatives[0].transcript
