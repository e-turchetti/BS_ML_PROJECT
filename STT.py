import queue
import re
import sys
from google.cloud import speech
from playsound import playsound
import pyaudio
from google.cloud.speech_v1 import types



# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self: object, rate: int = RATE, chunk: int = CHUNK) -> None:
        """The audio -- and generator -- is guaranteed to be on the main thread."""
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self: object) -> object:
        
        self._audio_interface = pyaudio.PyAudio()
        
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        
        return self

    def __exit__(
        self: object,
        type: object,
        value: object,
        traceback: object,
    ) -> None:
        """Closes the stream, regardless of whether the connection was lost or not."""
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()
        

    def _fill_buffer(
        self: object,
        in_data: object,
        frame_count: int,
        time_info: object,
        status_flags: object,
    ) -> object:
        """Continuously collect data from the audio stream, into the buffer.

        Args:
            in_data: The audio data as a bytes object
            frame_count: The number of frames captured
            time_info: The time information
            status_flags: The status flags

        Returns:
            The audio data as a bytes object
        """
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self: object) -> object:
        """Generates audio chunks from the stream of audio data in chunks.

        Args:
            self: The MicrophoneStream object

        Returns:
            A generator that outputs audio chunks.
        """
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def listen(client: object, streaming_config: object, called: bool, timeout_bool=True )-> str:


        #playsound('gne.mp3')
        '''
        if timeout_bool==True:
            responses = client.streaming_recognize(streaming_config, requests, timeout=5)
        else:
            responses = client.streaming_recognize(streaming_config, requests)
        '''
        count=0
        transcript=None
        while True:

            num_chars_printed = 0

            try:
                with MicrophoneStream(RATE, CHUNK) as stream:
       
                    audio_generator = stream.generator()
                    requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
                    if count==0:
                        count+=1
                        playsound('gne.mp3')
                    if timeout_bool==True:
                        responses = client.streaming_recognize(streaming_config, requests, timeout=5)
                    else:
                        responses = client.streaming_recognize(streaming_config, requests)
                    for response in responses:
                        
                        if not response.results:
                            continue
                    
                        # The `results` list is consecutive. For streaming, we only care about
                        # the first result being considered, since once it's `is_final`, it
                        # moves on to considering the next utterance.
                        result = response.results[0]
                        if not result.alternatives:
                            continue
                
                        # Display the transcription of the top alternative.
                        transcript = result.alternatives[0].transcript

                        # Display interim results, but with a carriage return at the end of the
                        # line, so subsequent lines will overwrite them.
                        #
                        # If the previous result was longer than this one, we need to print
                        # some extra spaces to overwrite the previous result
                        overwrite_chars = " " * (num_chars_printed - len(transcript))

                        if not result.is_final:
                            #sys.stdout.write(transcript + overwrite_chars + "\r")
                            #sys.stdout.flush()

                            num_chars_printed = len(transcript)
                            

                        else:
                            #if re.search(r"\b(stop)\b", transcript, re.I):
                            # print(transcript + overwrite_chars)
                                #break
        
                            if called==True and re.search(r'\s*mary\b', transcript, re.I) :
                                index=transcript.find("Mary")
                                transcript=transcript[index:]
                                print(transcript + overwrite_chars)
                                num_chars_printed = 0

                                return transcript
                            elif called==False:
                                if transcript.startswith('Mary') or transcript.startswith('mary'):
                                    transcript=transcript[5:]
                                print(transcript + overwrite_chars)
                                num_chars_printed = 0
                                return transcript
                            else:  
                                print(transcript)
                                break

                            

                    

                #return transcript
            except:
                print("error")
                return 



def main() -> None:



    """Transcribe speech from audio file."""
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "it-IT"  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(enable_automatic_punctuation=True,
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
        speech_contexts = [types.SpeechContext(phrases=['Mary'])]
    )
    # from google.protobuf import duration_pb2
   
    # activityTimeout = speech.StreamingRecognitionConfig.VoiceActivityTimeout()
    # activityTimeout.speech_start_timeout = duration_pb2.Duration(seconds=50)
    
    
    
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True,single_utterance=False,enable_voice_activity_events=True #, voice_activity_timeout=activityTimeout
        )

    # with MicrophoneStream(RATE, CHUNK) as stream:
    #     audio_generator = stream.generator()
    #     requests = (
    #         speech.StreamingRecognizeRequest(audio_content=content)
    #         for content in audio_generator
    #     )

    #     responses = client.streaming_recognize(streaming_config, requests)
    #     listen_print_loop(responses)
        # Now, put the transcription responses to use.
    listen(client,streaming_config,True,False)


if __name__ == "__main__":
    main()