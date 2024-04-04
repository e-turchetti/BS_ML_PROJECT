import TTS
import STT
import random 
import json
import re
import os
import shutil
import arduino_api_client1

'''
Un utente può:
-essere stato riconoscicuto tramite riconoscimento facciale/si è appena registrato e vuole fare la doccia-  recognized
-non è stato riconosciuto ma dice di essere registrato e ha fornito il proprio nome-  recognized_partially
-non è registrato ma vuole fare la doccia-  unknow


'''



def change_temperature(client_TTS,voice_TTS,audio_config,transcript: str,increase: bool,properties_api,thing_id,temp_desired_id,last_temp):    
    let_in_num = {
        "un": "1",    
        "uno": "1",
        "due": "2",
        "tre": "3",
        "quattro": "4",
        "cinque": "5",
        "sei": "6",
        "sette": "7",
        "otto": "8",
        "nove": "9",
        "dieci": "10"
    }
    transcript=transcript.split()
    degree = [let_in_num.get(word, word) for word in transcript]
    degree=[int(value) for value in degree if value.isdigit()]
    if degree==[]:
        degree=[2]
    if degree[0]==1:
        unit='grado'
    else: unit='gradi'
    if increase==True:
        action='aumento'
        if last_temp+degree[0]>40:
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Mi dispiace, non posso impostare una temperatura superiore ai 40 gradi" )  
            return 0
        arduino_api_client1.set_property(properties_api,thing_id,temp_desired_id,last_temp+degree[0])
    else: 
        action='diminuisco'
        if last_temp-int(degree[0])<20:
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Mi dispiace, non posso impostare una temperatura  inferiore ai 20 gradi" )  
            return 0
        arduino_api_client1.set_property(properties_api,thing_id,temp_desired_id,last_temp-degree[0])
    
    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ok, " +action+ " la temperatura di "  + str(degree[0])+unit ) 
    
    return  degree[0]



def shower(client_TTS,voice_TTS,audio_config,client_STT,streaming_config_STT,streaming_config_STT2 ,status: str,user_name):
    

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

    devices_api = arduino_api_client1.iot.DevicesV2Api(client_ino)
    properties_api=arduino_api_client1.iot.PropertiesV2Api(client_ino)
    thing_id,button_id= arduino_api_client1.get_properties_id(devices_api,"button")     
    thing_id,temp_desired_id= arduino_api_client1.get_properties_id(devices_api,"temp_desired")   

    button='off'
    if status=='unknow':
        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Perfetto")
        silence_temp=0
        no_temp=0
        wrong_temp=0
        while True:    
            if button=='on':
                break
            TTS.reproduce(client_TTS,voice_TTS,audio_config," Pronuncia la temperatura dell'acqua che vuoi. Essa deve essere compresa tra i 20 e i 40 gradi.")          
            default_temp=STT.listen(client_STT,streaming_config_STT,False)
            if default_temp=='stop':
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ok, a presto!")
                return 
            if default_temp==None:
                no_temp=0
                wrong_temp=0
                silence_temp+=1
                if silence_temp==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.Ricorda di parlare dopo il segnale acustico.")
                    continue
                else:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                    return 
            default_temp = re.search(r'\d+',default_temp )
            if default_temp==None:
                wrong_temp=0
                silence_temp=0
                no_temp+=1
                if no_temp==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non hai pronunciato un numero. Riprova per favore.")
                    continue
                else:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non sembra che tu sappia cosa sia un numero. Ritorna quando lo saprai!")
                    return 
            default_temp=default_temp.group()
            if int(default_temp)<20 or int(default_temp) >40:
                wrong_temp+=1
                silence_temp=0
                no_temp=0
                if wrong_temp==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"La temperatura scelta è oltre i limiti consentiti.")
                    continue
                else:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Forse è meglio che torni quando saprai cosa è un numero compreso tra 20 e 40. A presto!")
                    return 

            silence_temp2=0 # in realtà qui viene gestito anche se viene pronunciato qualcosa che non sia SI o No 
            while True:
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"La temperatura desiderata è "+default_temp+" gradi. è giusta?")
                transcript=STT.listen(client_STT,streaming_config_STT,False)
                if transcript=='stop':
                    return 
                if transcript==None:
                    silence_temp2+=1
                    if silence_temp2==1:
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.Ricorda di parlare dopo il segnale acustico.")
                        continue
                    else: return 
                if STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):    
                    silence_temp=0
                    break               
                elif STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così)\b", transcript, STT.re.I):   
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Perfetto.Allora apro l'acqua alla temperatura " + default_temp + " gradi. Buona doccia!")
                    default_temp=int(default_temp)
                    last_temp=default_temp
                    arduino_api_client1.set_property(properties_api,thing_id,button_id,True) 
                    arduino_api_client1.set_property(properties_api,thing_id,temp_desired_id,last_temp)
                    button='on'
                    break
                else:
                            silence_temp2+=1
                            if silence_temp2==2:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                                return 
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito!")
                            continue    
    if status=='recognized' or status=='recognized_partially':
        print(status)
        resp=["Perfetto, "," Era ora, ", "Ok, comincio ad impostare la temperatura dell'acqua, "]
        TTS.reproduce(client_TTS,voice_TTS,audio_config,random.choice(resp)+user_name)
        with open (f'./DB/{user_name}/temp.json') as temp_file:
            default_temp= str(json.load(temp_file)["temp"])
        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Apro l'acqua alla temperatura " + default_temp + " gradi. Buona doccia!")
        button='on'
        default_temp=int(default_temp)
        last_temp=default_temp
        arduino_api_client1.set_property(properties_api,thing_id,button_id,True) 
        arduino_api_client1.set_property(properties_api,thing_id,temp_desired_id,last_temp)
    
    
    while True:
        transcript=STT.listen(client_STT,streaming_config_STT2,True,False)
        if STT.re.match( r"\s*Mary\s+(chiudi|chiudi l'acqua|basta|ho finito|ho fatto|spegni|finito|fatto)\b", transcript, STT.re.I):
            button='off'
            arduino_api_client1.set_property(properties_api,thing_id,button_id,False) 
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Hai finito di fare la doccia?")
            count_silence_shower=0
            count_shower=0
            while True:
                transcript=STT.listen(client_STT,streaming_config_STT,False)
                if transcript=='stop':
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"ok. alla prossima!")
                    return
                if transcript==None:
                    if count_silence_shower==1:
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Lo prendo come un sì. Alla prossima!")
                        return
                    count_silence_shower+=1
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito nulla. Hai finito di fare la doccia?")
                    continue
                if STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così|ok)\b", transcript, STT.re.I):
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Perfetto.Alla prossima!")
                    return
                elif STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):  
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"ok. Quando vuoi ti riapro l'acqua!")
                    break
                else: 
                    count_shower+=1
                    if count_shower==1:
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito. hai finito di fare la doccia?")
                        continue
                    else: 
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Nel dubbio ci vediamo la prossima volta. Ciao!")
                        flag='finish'
                        return
        elif STT.re.match( r"\s*Mary\s+(stop)\b", transcript, STT.re.I):
            arduino_api_client1.set_property(properties_api,thing_id,button_id,False) 
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Alla prossima!")
            return
        elif STT.re.match( r"\s*Mary\s+(apri|apri l'acqua|ricominciamo|ricomincia|vai|continua|continuiamo|accendi l'acqua)\b", transcript, STT.re.I):
            if button=='on':
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"ehm, l'acqua è già aperta! Pensi di stare in una piscina?")
                continue
            if button=='off':
                arduino_api_client1.set_property(properties_api,thing_id,button_id,True) 
                arduino_api_client1.set_property(properties_api,thing_id,temp_desired_id,last_temp)
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Fatto!")
                continue
        elif STT.re.match( r"\s*Mary\s+(alza|aumenta|aumenti|alzi)\b", transcript, STT.re.I):
            
            deg=change_temperature(client_TTS,voice_TTS,audio_config,transcript,True,properties_api,thing_id,temp_desired_id,last_temp)
            prev_temp=last_temp
            last_temp+=deg
            print(last_temp)
        elif STT.re.match( r"\s*Mary\s+(abbassa|diminuisci|abbassi)\b", transcript, STT.re.I):
            deg=change_temperature(client_TTS,voice_TTS,audio_config,transcript,False,properties_api,thing_id,temp_desired_id,last_temp)
            prev_temp=last_temp
            last_temp-=deg
            print(last_temp)
        elif STT.re.search( r"\b(iniziale|inizialmente)\b", transcript, STT.re.I) and STT.re.search( r"\s*Mary\s+(ripristina|rimetti|reimposta|metti|vorrei|voglio|puoi rimettere|puoi ripristinare| puoi reimpostare| puoi mettere)\b", transcript, STT.re.I):
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Va bene, rimetto la temperatura iniziale di "+str(default_temp)+'gradi.')
            prev_temp=last_temp
            last_temp=default_temp
            print(last_temp)
            arduino_api_client1.set_property(properties_api,thing_id,temp_desired_id,last_temp)
        elif STT.re.search( r"\b(di prima|precedente|antecedente|prima|a prima|)\b", transcript, STT.re.I) and STT.re.search( r"\s*Mary\s+(ripristina|rimetti|reimposta|metti|vorrei|voglio|puoi rimettere|puoi ripristinare| puoi reimpostare| puoi mettere|imposta)\b", transcript, STT.re.I):
            tmp=prev_temp
            last_temp= tmp
            prev_temp=last_temp
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Va bene, rimetto la temperatura a "+str(prev_temp)+'gradi.')
            arduino_api_client1.set_property(properties_api,thing_id,temp_desired_id,last_temp)
            print(last_temp)
        else:
            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito. ")
    

def no_shower(client_TTS,voice_TTS,audio_config,client_STT,streaming_config_STT, status:str,user_name):
    flag=""
    if status=='recognized':
        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Vuoi modificare i tuoi dati?")
        count_silence_data=0
        count_data=0
        while True:
            transcript=STT.listen(client_STT,streaming_config_STT,False)
            if transcript=='stop':
                return
            if transcript==None:
                if count_silence_data==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                    return
                count_silence_data+=1
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito nulla. Vuoi modificare i tuoi dati?")
                continue
            if STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così|ok)\b", transcript, STT.re.I):
                flag=""
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Bene. Vuoi modificare la tua temperatura preferita, il tuo nome, oppure vuoi cancellare i tuoi dati?")
                count_silence_modify=0
                count_modify=0
                while True:
                    if flag=='modify_more':
                                break 
                    transcript=STT.listen(client_STT,streaming_config_STT,False)
                    if transcript=='stop':
                        return
                    if transcript==None:
                        if count_silence_modify==1:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                            return
                        count_silence_modify+=1
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito nulla. Quali dati vuoi modificare?")
                        continue
                    if STT.re.search(r"\b(temperatura|temperatura preferita|la prima|prima|primo)\b", transcript, STT.re.I):
                        silence_temp=0
                        no_temp=0
                        wrong_temp=0
                        while True:
                            if flag=='modify_more':
                                break    
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Pronuncia la nuova temperatura.Ricorda che deve essere tra i 20 e i 40 gradi.")          
                            temp=STT.listen(client_STT,streaming_config_STT,False)
                            if temp=='stop':
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ok, interrompo. A presto!")
                                return 
                            if temp==None:
                                no_temp=0
                                wrong_temp=0
                                silence_temp+=1
                                if silence_temp==1:
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.Ricorda di parlare dopo il segnale acustico. ")
                                    continue
                                else:
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                                    return 
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
                                    return 
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
                                    return 

                            silence_temp2=0 # in realtà qui viene gestito anche se viene pronunciato qualcosa che non sia SI o No 
                            while True:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"La tua nuova temperatura preferita è "+temp+" gradi. è giusta?")
                                transcript=STT.listen(client_STT,streaming_config_STT,False)
                                if transcript=='stop':
                                    return 
                                if transcript==None:
                                    silence_temp2+=1
                                    if silence_temp2==1:
                                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.")
                                        continue
                                    else: return 

                                if STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):    
                                    silence_temp=0
                                    break                
                                elif STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così)\b", transcript, STT.re.I):
                                    path = os.path.join("./DB",user_name) 
                                    with open(os.path.join(path,'temp.json'), "r") as outfile:
                                            json_data = json.load(outfile)
                                            json_data['temp'] = str(temp)
                                    with open(os.path.join(path,'temp.json'), 'w') as outfile:
                                        outfile.write(json.dumps(json_data))    
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Perfetto, la tua temperatura preferita è stata aggiornata.Vuoi modificare altri dati?")
                                    flag='modify_more'
                                    break
                                else:
                                    silence_temp2+=1
                                    if silence_temp2==2:
                                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                                        return 
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito!")
                                    continue
                                
                    elif STT.re.search(r"\b(nome|user name|appellativo|nickname)\b", transcript, STT.re.I):  
                        silence_name=0
                        while True:
                            if flag=='modify_more':
                                break 
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Pronuncia il tuo nuovo nome!")
                            name=STT.listen(client_STT,streaming_config_STT,False)
                            if name=='stop':
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ok, interrompo. A presto!")
                                return 
                            if name==None:
                                silence_name+=1
                                if silence_name==1:
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.")
                                    continue
                                else:
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                                    return 

                            silence_name2=0 # in realtà qui viene gestito anche se viene pronunciato qualcosa che non sia SI o No 
                            while True:
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Il tuo nuovo nome è "+name+". è corretto?")
                                transcript=STT.listen(client_STT,streaming_config_STT,False)
                                if transcript=='stop':
                                    return 
                                if transcript==None:
                                    silence_name2+=1
                                    if silence_name2==1:
                                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.")
                                        continue
                                    else: return 
                                if STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):    
                                    silence_name=0
                                    break                
                                elif STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così)\b", transcript, STT.re.I):
                                    if name==user_name:
                                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ma già ti chiami così!")
                                        silence_name=0
                                        break
                                    users_list=[ item for item in os.listdir('./DB') if os.path.isdir(os.path.join('./DB', item))]
                                    if name in users_list:
                                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ops!. Già esiste un utente con questo nome. Utilizzane un altro per favore!")
                                        silence_name=0
                                        break 
                                    os.rename("./DB/"+user_name,"./DB/"+name)
                                    model_name="Facenet512"
                                    file_name = f"representations_{model_name}.pkl"
                                    file_name = file_name.replace("-", "_").lower()
                                    os.remove(f"./DB/{file_name}")
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Perfetto,il tuo nome è stato aggiornato.Vuoi modificare altri dati?")
                                    user_name=name
                                    flag='modify_more'
                                    break
                                else:
                                    silence_name2+=1
                                    if silence_name2==2:
                                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                                        return 
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito!")
                                    continue
                    elif STT.re.search (r"\b(eliminare|eliminazione|cancellare|cancellazione|elimina|elimini|cancella|cancelli|rimuovere|rimuovi|cancellati|eliminati|rimossi)\b", transcript, STT.re.I):  
                        silence_canc=0
                        while True:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sicuro di voler eliminare definitivamente i tuoi dati?")
                            transcript=STT.listen(client_STT,streaming_config_STT,False)
                            if transcript=='stop':
                                return 
                            if transcript==None:
                                silence_canc+=1
                                if silence_canc==1:
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito niente.")
                                    continue
                                else: return 
                            if STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):    
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Ne sono entusiasta. Allora ci vediamo alla prossima doccia!")
                                return             
                            elif STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così)\b", transcript, STT.re.I):
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Va bene, elimino i tuoi dati. Spero di rivederti. Alla prossima!")
                                    shutil.rmtree("./DB/"+user_name)
                                    model_name="Facenet512"
                                    file_name = f"representations_{model_name}.pkl"
                                    file_name = file_name.replace("-", "_").lower()
                                    os.remove(f"./DB/{file_name}")
                                    return
                            else:
                                silence_canc+=1
                                if silence_canc==2:
                                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                                    return 
                                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito!")
                                continue
                        

                    else: 
                        count_modify+=1
                        if count_modify==1:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito. Quali dati vuoi modificare?")
                            continue
                        else: 
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                            return
                # with open (f'./DB/{user_name}/temperature.json') as temp_file:
                #     default_temp= str(json.load(temp_file)["default"])
            elif STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):  
                if flag=='modify_more':
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"ok, alla prossima!")
                    return
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Vuoi avere informazioni sul funzionamento del sistema?")
                count_silence_info=0
                count_info=0
                while True:
                    transcript=STT.listen(client_STT,streaming_config_STT,False)
                    if transcript=='stop':
                        return
                    if transcript==None:
                        if count_silence_info==1:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                            return
                        count_silence_info+=1
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito nulla. Vuoi avere informazioni sul funzionamento del sistema?")
                        continue
                    if STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così|ok)\b", transcript, STT.re.I):
                        TTS.reproduce(client_TTS,voice_TTS,audio_config," Io mi chiamo Mary, e sono una doccia intelligente. Se sei già registrato nel sistema, sono in grado di riconoscerti e di aprire l'acqua alla tua temperatura preferita. Se non sei registrato, posso comunque prepararti la doccia alla temperatura che vuoi. Mentre ti stai facendo la doccia, puoi chiedermi ad esempio di abbassare o alzare la temperatura, o di aprire o chiudere l'acqua. L'importante è che mi chiami per nome, e mi dici cosa vuoi fare. Dunque puoi dirmi  ad esempio 'Mary, chiudi l'acqua', e io chiuderò l'acqua. Al contrario, quando non stai facendo la doccia, puoi rispondere alle mie richieste senza chiamarmi per nome. Dunque, se ti chiedo, ad esempio, 'Pronuncia la tua temperatura preferita', puoi rispondere con un numero, senza chiamarmi per nome. In generale devi prestare attenzione a 2 semplici regole: innanzitutto ricordati di parlare dopo il segnale acustico, altrimenti non potrò sentirti. Inoltre, ogni volta che ti sto ascoltando, se pronunci la parola STOP, interromperò qualsiasi cosa stiamo facendo. Spero di essere stata chiara. In ogni caso non preoccuparti, cercherò sempre di interagire in maniera semplice e chiara. Ci vediamo presto!")
                        
                        return
                    elif STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):  
                        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Beh se non vuoi ne fare la doccia, ne modificare i tuoi dati,ne avere informazioni, non c'è molto altro che posso fare per te. A presto!")
                        return
 
                    else: 
                        count_info+=1
                        if count_info==1:
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito. vuoi avere informazioni sul sistema?")
                            continue
                        else: 
                            TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                            return

            
            else: 
                count_data+=1
                if count_data==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito. vuoi modificare i tuoi dati?")
                    continue
                else: 
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                    return
    if status=='recognized_partially':
        TTS.reproduce(client_TTS,voice_TTS,audio_config,"Vuoi avere informazioni sul funzionamento del sistema?")
        count_silence_info=0
        count_info=0
        while True:
            transcript=STT.listen(client_STT,streaming_config_STT,False)
            if transcript=='stop':
                return
            if transcript==None:
                if count_silence_info==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Sembra tu non abbia voglio di parlare! Ci vediamo quando ti andrà.")
                    return
                count_silence_info+=1
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Non ho sentito nulla. Vuoi avere informazioni sul funzionamento del sistema?")
                continue
            if STT.re.match(r"\b(si|sì|esatto|altro che|altroché|certamente|certo|sicuramente|sicuro|Naturalmente|assolutamente sì|eccome|senz'altro|proprio così|ok)\b", transcript, STT.re.I):
                TTS.reproduce(client_TTS,voice_TTS,audio_config," Io mi chiamo Mary, e sono una doccia intelligente. Se sei già registrato nel sistema, sono in grado di riconoscerti e di aprire l'acqua alla tua temperatura preferita. Se non sei registrato, posso comunque prepararti la doccia alla temperatura che vuoi. Mentre ti stai facendo la doccia, puoi chiedermi ad esempio di abbassare o alzare la temperatura, o di aprire o chiudere l'acqua. L'importante è che mi chiami per nome, e mi dici cosa vuoi fare. Dunque puoi dirmi  ad esempio 'Mary, chiudi l'acqua', e io chiuderò l'acqua. Al contrario, quando non stai facendo la doccia, puoi rispondere alle mie richieste senza chiamarmi per nome. Dunque, se ti chiedo, ad esempio, 'Pronuncia la tua temperatura preferita', puoi rispondere con un numero, senza chiamarmi per nome. In generale devi prestare attenzione a 2 semplici regole: innanzitutto ricordati di parlare dopo il segnale acustico, altrimenti non potrò sentirti. Inoltre, ogni volta che ti sto ascoltando, se pronunci la parola STOP, interromperò qualsiasi cosa stiamo facendo. Spero di essere stata chiara. In ogni caso non preoccuparti, cercherò sempre di interagire in maniera semplice e chiara.Ci vediamo presto! ")
                return
            elif STT.re.match(r"\b(no|niente affatto|assolutamente no|proprio no|non esattamente|non proprio|mai|non credo)\b", transcript, STT.re.I):  
                TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, ma non essendo stato riconosciuto tramite il riconoscimento facciale non posso permetterti di fare altro. Prova ad effetuarlo di nuovo!")
                return

            else: 
                count_info+=1
                if count_info==1:
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa, non ho capito. vuoi avere informazioni sul sistema?")
                    continue
                else: 
                    TTS.reproduce(client_TTS,voice_TTS,audio_config,"Scusa ma non ti capisco proprio. Torna quando avrai le idee più chiare!")
                    return    
        

