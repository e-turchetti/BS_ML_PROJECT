import cv2
from deepface.detectors import FaceDetector
import time
import TTS
import STT
import os
import json
import re



def enroll(client_TTS,voice_TTS,audio_config,client_STT,streaming_config_STT,detector_backend="opencv",model_name='Facenet512'):

    users_list=[ item for item in os.listdir('./DB') if os.path.isdir(os.path.join('./DB', item))]
    silence_name=0
    while True:
        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Pronuncia il tuo nome!")
        name=STT.listen(client_STT,streaming_config_STT,False)
        if name=='stop':
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ok, interrompo la registrazione. A presto!")
            return False
        if name==None:
            silence_name+=1
            if silence_name==1:
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente. Ricorda di parlare dopo il segnale acustico!")
                continue
            else:
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                return False

        silence_name2=0 # in realtà qui viene gestito anche se viene pronunciato qualcosa che non sia SI o No 
        while True:
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Il tuo nome è "+name+". è corretto?")
            transcript=STT.listen(client_STT,streaming_config_STT,False)
            if transcript=='stop':
                return False
            if transcript==None:
                silence_name2+=1
                if silence_name2==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.Aspetta il segnale acustico prima di parlare.")
                    continue
                else: return False
            if STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):    
                silence_name=0
                break                
            elif STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così)\b", transcript, STT.re.I):
                if name in users_list:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ops!. Già esiste un utente con questo nome. Utilizzane un altro per favore!")
                    silence_name=0
                    break
                silence_temp=0
                no_temp=0
                wrong_temp=0
                while True:    
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Pronuncia la tua temperatura dell'acqua preferita.Ricorda che deve essere tra i 20 e i 40 gradi.")          
                    temp=STT.listen(client_STT,streaming_config_STT,False)
                    if temp=='stop':
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ok, interrompo la registrazione. A presto!")
                        return False
                    if temp==None:
                        no_temp=0
                        wrong_temp=0
                        silence_temp+=1
                        if silence_temp==1:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.")
                            continue
                        else:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                            return False
                    temp = re.search(r'\d+',temp )
                    if temp==None:
                        wrong_temp=0
                        silence_temp=0
                        no_temp+=1
                        if no_temp==1:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non hai pronunciato un numero. Riprova per favore.")
                            continue
                        else:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non sembra che tu sappia cosa sia un numero. Ritorna quando lo saprai!")
                            return False
                    temp=temp.group()
                    if int(temp)<20 or int(temp) >40:
                        wrong_temp+=1
                        silence_temp=0
                        no_temp=0
                        if wrong_temp==1:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"La temperatura scelta è oltre i limiti consentiti.")
                            continue
                        else:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Forse è meglio che torni quando saprai cosa è un numero compreso tra 20 e 40. A presto!")
                            return False

                    silence_temp2=0 # in realtà qui viene gestito anche se viene pronunciato qualcosa che non sia SI o No 
                    while True:
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"La tua temperatura preferita è "+temp+" gradi. è giusta?")
                        transcript=STT.listen(client_STT,streaming_config_STT,False)
                        if transcript=='stop':
                            return False
                        if transcript==None:
                            silence_temp2+=1
                            if silence_temp2==1:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.")
                                continue
                            else: return False
                        if STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):    
                            silence_temp=0
                            break                
                        elif STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così)\b", transcript, STT.re.I):                            
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Procediamo con l'acquisizione del volto. Una volta iniziata questa fase, la registrazione non potrà essere interrotta.")
                            silence_continue=0
                            while True:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Vuoi continuare con la registrazione?")
                                transcript=STT.listen(client_STT,streaming_config_STT,False)
                                if transcript=='stop':
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ok. Alla prossima!")
                                    return False
                                if transcript==None:
                                    silence_continue+=1
                                    if silence_continue==1:
                                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.Ricordati di parlare dopo il segnale acustico.")
                                        continue
                                    else: return False
                                if STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo|non voglio)\b", transcript, STT.re.I):
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ok. Alla prossima!")
                                    return False
                                elif STT.re.match(r"\b(continuiamo|andiamo avanti|procediamo|si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così| ok)\b", transcript, STT.re.I):
                                    #potrebbe essere necessario spostare queste 4 righe di codice sotto
                                    path = os.path.join("./DB", name) 
                                    os.mkdir(path) 
                                    with open(os.path.join(path,'temp.json'), "w") as outfile:
                                            outfile.write(json.dumps({ "temp": int(temp)}))

                                    cap = cv2.VideoCapture(0)
                                    count_fail=0
                                    count_pic=0
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Bene. Guarda la fotocamera con un volto neutrale.")
                                    while True:
                                        if count_pic==3:
                                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Perfetto "+name+". La registrazione è stata completata con successo!")
                                            file_name = f"representations_{model_name}.pkl"
                                            file_name = file_name.replace("-", "_").lower()
                                            os.remove(f"./DB/{file_name}")
                                            return name                              
                                        elif count_pic==1:
                                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Bene. Ora fai un sorriso!")
                                        elif count_pic==2:
                                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Wow, quanta bellezza! Ora allontànati leggermente dalla fotocamera, continuando a guardarla.")
                                        while True:
                                            TIMER = int(3)
                                            # Read and display each frame
                                            ret, img = cap.read()
                                            cv2.imshow('Enroll', img)

                                            prev = time.time()
                                            while TIMER >= 0:
                                                    ret, img = cap.read()

                                                    cv2.rectangle(img, (10, 10), (90, 50), (67, 67, 67), -10)
                                                    cv2.putText(img,
                                                        str(TIMER),
                                                        (40, 40),
                                                        cv2.FONT_HERSHEY_SIMPLEX,
                                                        1,
                                                        (255, 255, 255),
                                                        1,)
                                                    cv2.imshow('Enroll', img)
                                                    cv2.waitKey(125)

                                                    # current time
                                                    cur = time.time()

                                                    # Update and keep track of Countdown
                                                    # if time elapsed is one second
                                                    # then decrease the counter
                                                    if cur-prev >= 1:
                                                        prev = cur
                                                        TIMER = TIMER-1

                                            else:
                                                    ret, img = cap.read()
                                                    align=True
                                                    face_detector = FaceDetector.build_model(detector_backend)
                                                    face_objs1 = FaceDetector.detect_faces(face_detector, detector_backend, img, align)
                                                    print(len(face_objs1))
                                                    if len(face_objs1)==1:
                                                    # Display the clicked frame for 2
                                                    # sec.You can increase time in
                                                    # waitKey also
                                                        cv2.imshow('Enroll', img)

                                                        # time for which image displayed
                                                        cv2.waitKey(2000)

                                                        # Save the frame
                                                        cv2.imwrite(os.path.join(path,'foto'+str(count_pic)+'.jpg'), img)
                                                        count_pic+=1
                                                        break



                                                    else:
                                                        count_fail+=1
                                                        if count_fail==2:
                                                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non riesco ad individuare un volto. Prova ad eliminare eventuali oggetti che ostruiscono il volto e a variare leggermente la distanza dalla videocamera, assicurandoti di continuare a guardarla.")
                                                            count_fail=0

                                else:
                                    silence_continue+=1
                                    if silence_continue==2:
                                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                                        return False
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito!")
                                    continue
                                
                        else:
                            silence_temp2+=1
                            if silence_temp2==2:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                                return False
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito!")
                            continue
                        
            else:
                silence_name2+=1
                if silence_name2==2:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                    return False
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito!")
                continue

                        

    
