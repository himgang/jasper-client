import io
import os
import google.cloud as cloud


def transcribe(fp):
    # Instantiates a client
    client = cloud.speech.SpeechClient()

    # The name of the audio file to transcribe
    file_name = fp
    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = cloud.speech.types.RecognitionAudio(content=content)

    config = google.cloud.speech.types.RecognitionConfig(
        encoding=cloud.speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US')

    # Detects speech in the audio file
    response = client.recognize(config, audio)
    
    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))
    text = result.alternatives[0].transcript
    return text
        
        
        
        