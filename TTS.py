"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
from playsound import playsound


def reproduce(client_TTS:object, voice:object,audio_config:object,text: str):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    response = client_TTS.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

    with open("output.mp3", "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"') 

    playsound("output.mp3")

    return 
