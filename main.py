
import STT
import TTS
import deepface1.deepface.DeepFace as DeepFace
import os
import json
from google.cloud.speech_v1 import types   
import enrollment 

import shower



def main() -> None:
    #Useful parameters
    language_code = "it-CH"

    # Audio recording parameters
    RATE = 16000
    CHUNK = int(RATE / 10)  # 100ms
    '''
    #Arduino client and configurations

    oauth_client_ino= arduino_api_client1.BackendApplicationClient(client_id='pFcckSqU1WFGlm80UjDWSQfpNp1c6X1G')
    token_url = "https://api2.arduino.cc/iot/v1/clients/token"

    oauth = arduino_api_client1.OAuth2Session(client=oauth_client_ino)
    token = oauth.fetch_token(
        token_url=token_url,
        client_id='pFcckSqU1WFGlm80UjDWSQfpNp1c6X1G',
        client_secret='ndYh4cjpPB260TBd6ffC2vrox2PDDY2CNnCih6j94JSNTfIi3h5n0LDDFZNWKh9X',
        include_client_id=True,
        audience="https://api2.arduino.cc/iot",
    )

    access_token = token.get("access_token")

    client_config = arduino_api_client1.Configuration(host="https://api2.arduino.cc/iot")
    client_config.access_token = access_token
    client_ino = arduino_api_client1.iot.ApiClient(client_config)
    '''
    #Speech to text client
    client_STT = STT.speech.SpeechClient()
    #Text to speech client
    client_TTS = TTS.texttospeech.TextToSpeechClient()
    
        #Speech to text configurations
    config_STT = STT.speech.RecognitionConfig(enable_automatic_punctuation=True,
        encoding=STT.speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
        speech_contexts = [types.SpeechContext(phrases=['Mary abbassa la temperatura'])]
        )

    streaming_config_STT = STT.speech.StreamingRecognitionConfig(
        config=config_STT, interim_results=True,single_utterance=True,enable_voice_activity_events=True)
    streaming_config_STT2 = STT.speech.StreamingRecognitionConfig(
        config=config_STT, interim_results=True,single_utterance=False,enable_voice_activity_events=True)
    
    #Text to speech configurations 

    voice_TTS = TTS.texttospeech.VoiceSelectionParams(
        language_code="IT-IT", name='it-IT-Wavenet-B')

    audio_config = TTS.texttospeech.AudioConfig(
        audio_encoding=TTS.texttospeech.AudioEncoding.MP3)

    users_list=[ item for item in os.listdir('./DB') if os.path.isdir(os.path.join('./DB', item))]

    def wan2_shower(status,user_name):
        nonlocal flag
        count_silence_shower=0
        count_shower=0
        while True:
            transcript=STT.listen(client_STT,streaming_config_STT,False)
            if transcript=='stop':
                flag='finish'
                return
            if transcript==None:
                if count_silence_shower==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                    flag='finish'
                    return
                count_silence_shower+=1
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito nulla. Vuoi fare la doccia "+user_name+"?")
                continue
            if STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così|ok|voglio farla|voglio fare la doccia|vorrei farla|vorrei fare la doccia|vorrei lavarmi|voglio lavarmi)\b", transcript, STT.re.I):
                shower.shower(client_TTS,voice_TTS,audio_config,client_STT,streaming_config_STT,streaming_config_STT2 ,status,user_name) #recognized=False
                flag='finish'
                return
            elif STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo|non voglio)\b", transcript, STT.re.I):  
                shower.no_shower(client_TTS,voice_TTS,audio_config,client_STT,streaming_config_STT,status,user_name)
                flag='finish'
                return  
            else: 
                count_shower+=1
                if count_shower==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito. vuoi fare la doccia?")
                    continue
                else: 
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                    flag='finish'
                    return 
    while True:
        flag=""
        label= DeepFace.stream(db_path = "/home/user/Scrivania/Biometric systems/ProgettoFinal/DB",enable_face_analysis = False,
        time_threshold=1,frame_threshold=1,recognition_times=3,source=0,detector_backend="opencv",model_name='Facenet512')
        if label==None:

            TTS.reproduce(client_TTS,voice_TTS,audio_config, "Ciao, credo che non ci conosciamo. Sei già registrato nel sistema?")
            count_registered=0
            while True:
                if flag=='finish':
                    break
                
                if count_registered==2:
                    break                  
                
                transcript=STT.listen(client_STT,streaming_config_STT,False)  
                
                if transcript=='stop' or transcript==None: # se viene pronunciata la parola Stop oppure niente, ricomincia da capo 
                    flag='finish'
                    break
                if STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Sono registrata|Sono registrato|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così)\b", transcript, STT.re.I):
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ah, perdonami, non ti ho riconosciuto. Pronuncia il nome con il quale ti sei registrato  per favore.")
                    count_name=0
                    count_silence_name=0
                    while True:
                        if flag=='finish':
                            break   
                        if count_name==2:
                            flag='finish'
                            break

                        user_name=STT.listen(client_STT,streaming_config_STT,False)
                        
                        if user_name=='stop':
                            flag='finish'
                            break
                        if user_name==None:
                            if count_silence_name==1:
                                flag='finish'
                                break
                            count_silence_name+=1
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito nulla. Pronuncia il tuo nome per favore.")
                            continue
                            
                        if user_name in users_list:     
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ok "+user_name+". Vuoi fare la doccia?")
                            wan2_shower("recognized_partially",user_name)
                            break
                        else: 
                            if count_name==1:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non mi risulta un utente con il nome "+user_name+". Prova a effettuare di nuovo il riconoscimento facciale.")
                                count_name+=1
                                continue
                            else:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non mi risulta un utente con il nome "+user_name+". Assicurati di pronunciare solamente il tuo nome, e non altre parole. ")
                                count_name+=1
                                continue
                elif STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo|non sono registrato|non sono registrata|non lo sono)\b", transcript, STT.re.I):
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Vuoi registrarti, fare la doccia, o avere informazioni sul funzionamento del sistema?")
                    count_silence_shower=0
                    count_shower=0
                    while True:
                        transcript=STT.listen(client_STT,streaming_config_STT,False)
                        if transcript=='stop':
                            flag='finish'
                            break
                        if transcript==None:
                            if count_silence_shower==1:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                                flag='finish'
                                break
                            count_silence_shower+=1
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito nulla. Ricordati di parlare dopo il segnale acustico. Vuoi registrarti, vuoi fare la doccia, o vuoi riascoltare le informazioni sul sistema?")
                            continue
                        if STT.re.search(r"\b(Doccia|Docciare|Lavarmi|Lavare)\b", transcript, STT.re.I):
                            shower.shower(client_TTS,voice_TTS,audio_config,client_STT,streaming_config_STT,"unknow","") #recognized=False
                            flag='finish'
                            break
                        elif STT.re.search(r"\b(Voglio registrarmi|Vorrei registrarmi|Registrazione|Registrarmi|Mi piacerebbe registrarmi|Registrare|Io voglio registrarmi|Io vorrei registrarmi|Vorrei effettuare la registrazione)\b", transcript, STT.re.I):
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Bene, allora procediamo con la registrazione.")
                                user_name=enrollment.enroll(client_TTS,voice_TTS,audio_config,client_STT,streaming_config_STT)
                                if user_name==False:
                                    flag='finish'
                                    break
                                else:                                   
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config, user_name+" vuoi fare la doccia?")
                                    wan2_shower("recognized",user_name)
                                    break     
                        elif STT.re.search(r"\b(info|informazioni|informazione|informare|chiarimento|chiarimenti|delucidazioni|delucidazione|informativa|informami|indicazione|indicazioni)\b", transcript, STT.re.I):                  
                            TTS.reproduce(client_TTS,voice_TTS,audio_config, "Io mi chiamo Mary, e sono una doccia intelligente. Se sei già registrato nel sistema, sono in grado di riconoscerti e di aprire l'acqua alla tua temperatura preferita. Se non sei registrato, posso comunque prepararti la doccia alla temperatura che vuoi. Mentre ti stai facendo la doccia, puoi chiedermi ad esempio di abbassare o alzare la temperatura, o di aprire o chiudere l'acqua. L'importante è che mi chiami per nome, e mi dici cosa vuoi fare. Dunque puoi dirmi  ad esempio 'Mary, chiudi l'acqua', e io chiuderò l'acqua. Al contrario, quando non stai facendo la doccia, puoi rispondere alle mie richieste senza chiamarmi per nome. Dunque, se ti chiedo, ad esempio, 'Pronuncia la tua temperatura preferita', puoi rispondere con un numero, senza chiamarmi per nome. In generale devi prestare attenzione a 2 semplici regole: innanzitutto ricordati di parlare dopo il segnale acustico, altrimenti non potrò sentirti. Inoltre, ogni volta che ti sto ascoltando, se pronunci la parola STOP, interromperò qualsiasi cosa stiamo facendo. Spero di essere stata chiara. In ogni caso non preoccuparti, cercherò sempre di interagire in maniera semplice e chiara.  ")
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Adesso che cosa vuoi fare? Vuoi registrarti,  fare la doccia, o riascoltare le informazioni sul funzionamento del sistema?")
                        
                        else: 
                            count_shower+=1
                            if count_shower==1:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito. Vuoi registrarti o vuoi fare la doccia?")
                                continue
                            else: 
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                                flag='finish'
                                break                   
               
                else: 
                    count_registered+=1
                    if count_registered==1:
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito. Sei già registrato nel sistema?")
                        continue
                    else: 
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco. Proviamo a ricominciare.")
                        continue

        else:
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ciao "+label+". Vuoi fare la doccia?")
            wan2_shower("recognized",label)
            
                        
if __name__ == "__main__":
    main()