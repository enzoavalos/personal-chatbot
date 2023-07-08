# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet,FollowupAction
from swiplserver import PrologMQI,PrologThread
import os.path
from time import sleep
import random
from .jsonUtils import *
from .jokes import getGeekJoke
from .dates import *
from .wikipediaApi import getInfoAboutTopic
import requests
from urllib.request import urlopen

class ActionTellJoke(Action):
    def name(self) -> Text:
       return "action_tell_joke"
    
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_msg = tracker.latest_message
        ManipularDatosRegistrados.saveMessageOfInterest(last_msg['metadata'])
        dispatcher.utter_message(text="Nada que un chiste no pueda arreglar")
        dispatcher.utter_message(text=getGeekJoke())
        return []

class ActionDespedida(Action):
   def name(self) -> Text:
       return "action_despedida"
   def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        chat_id = tracker.latest_message['metadata']['message']['chat']['id']
        saludo=random.choice(["Hasta luego","Nos vemos", "Chau","Hasta pronto"])
        dispatcher.utter_message(text=saludo)
        sendSticker(chat_id, "CAACAgUAAxkBAAEZPexjUzGygnj1BXmZo2s-HtP2bXl4XQACggMAAukKyAOMWQOx6VvEtyoE")
        return []

class ActionCheckWhenFree(Action):
    def name(self) -> Text:
       return "action_check_when_free"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        msg_received_id = tracker.latest_message['metadata']['message']['message_id']
        dia = getCurrentWeekDay()
        with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async("consult('C:/Users/Usuario/ProyectosRasa/bot_personal_grupal/actions/hechos.pl')", find_all=False)
                    prolog_thread.query_async(f"actividades_dia({dia},X).",find_all=True)
                    sleep(0.1)
                    today_result = prolog_thread.query_async_result()
                    if today_result:
                        max_hr = 0
                        for item in today_result:
                            if int(item['X']) > max_hr:
                                max_hr = int(item['X'])
                        dispatcher.utter_message(text="Yo hoy puedo desde de las "+str(max_hr),response_id=msg_received_id)
                    else:
                        dispatcher.utter_message(text="Cuando quieran, hoy estoy libre",response_id=msg_received_id)
        return []

class ActionAnswerMeetingProposal(Action):
    def name(self) -> Text:
       return "action_answer_meeting_proposal"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_from = tracker.latest_message['metadata']['message']['from']['first_name']
        meetings = ManipularDatosRegistrados.getMeetingsList()
        if(meetings == None):
            dispatcher.utter_message(text="Es verdad, hay que organizarnos")
        else:
            meet_day = str(list(meetings)[0])
            meet_time = str(meetings[meet_day]['time'])
            dispatcher.utter_message(text="Ya habiamos quedado para el "+meet_day+" a las "+meet_time+", "+str(user_from))
        
        return []


class ActionPinTopicQuestion(Action):
    def name(self) -> Text:
       return "action_pin_topic_question"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        msgOfInterest = ManipularDatosRegistrados.getMessageOfInterest()
        if(msgOfInterest != None):
            dispatcher.utter_message(text="Lastima, fijo el mensaje por si alguien mas te puede ayudar")
            pinMessage(msgOfInterest['message']['chat']['id'], msgOfInterest['message']['message_id'])
        else:
            dispatcher.utter_message(text="Lastima, capaz alguien mas te puede ayudar")
        
        return []

class ActionIncomingMeetings(Action):
    def name(self) -> Text:
       return "action_incoming_meetings"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_from = tracker.latest_message['metadata']['message']['from']['username']
        meetings = ManipularDatosRegistrados.getMeetingsList()
        if(meetings == None):
            dispatcher.utter_message(text=f'@{user_from} no arreglamos nada todavia')
        else:
            msg = "Proximas reuniones:\n"
            for dia in meetings:
                hora = meetings[dia]['time']
                msg += f'{dia} {hora}hs\n'
            dispatcher.utter_message(text=msg+f'\n\n@{user_from} ahi tenes')
        
        return []

class ActionScheduleMeeting(Action):
    def name(self) -> Text:
       return "action_schedule_meeting"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if(tracker.get_slot("free_to_meet") == False):
            dispatcher.utter_message(text="Todavia no arreglamos nada")
            return []

        ManipularDatosRegistrados().increaseParticipants()
        cant = ManipularDatosRegistrados().getCurrentAmountRegistered()
        last_msg = tracker.latest_message
        memberCount = getChatMemberCount(last_msg['metadata']['message']['chat']['id'])
        print("cant registrados "+str(cant))
        print("cant miembros "+str(memberCount))
        if(int(cant) < memberCount-1):
            return [FollowupAction('action_listen')]
        dia = tracker.get_slot("weekday")
        hora = tracker.get_slot("hour_of_day")
        if(dia == None):
            dia = getCurrentWeekDay()
        else:
            dia = str(dia)
        
        if(ManipularDatosRegistrados.checkDateIsFree(dia, hora)):
            desc = "Reunion: "+dia+" "+hora+"hs"
            ManipularDatosRegistrados.saveMeeting(dia, hora)
            setNewDescription(last_msg['metadata']['message']['chat']['id'],desc)
            dispatcher.utter_message(text="Perfecto, ya que todos estan de acuerdo quedamos el "+dia+" a las "+str(hora)+"\n\nYa lo agende en la descripcion")
        else:
            dispatcher.utter_message(text="Me acabo de dar cuenta que tenemos una reunion que se superpone\n\nArreglemos para otro momento")

        return [SlotSet('free_to_meet',False),SlotSet('hour_of_day',None),SlotSet('time_of_day',None),FollowupAction('action_listen')]

class ActionGladYouLiked(Action):
    def name(self) -> Text:
       return "action_glad_you_liked"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        chat_id = tracker.latest_message['metadata']['message']['chat']['id']
        sticker_id = random.choice(["CAACAgUAAxkBAAEZPeVjUzDQ7hw5WjPryWN_dA_6W1a1jQACbgMAAukKyAN8NA8_2uwEbSoE",
            "CAACAgUAAxkBAAEZPfNjUzOjt-Z8mB8PHb_W1kWYXt7dYgACbwMAAukKyAOvzr7ZArpddCoE",
            "CAACAgUAAxkBAAEZPfxjUzPakSEKlWlz6CHOdskt6H3LLwAChAEAArjfQFed4jY_fWKaFCoE"])
        sendSticker(chat_id, sticker_id)
        return []

class ActionKnowsAboutTopic(Action):
   def name(self) -> Text:
       return "action_knows_about_topic"
   def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tema_discusion = str(tracker.get_slot("topic_to_discuss"))
        palabras_clave = tema_discusion.split()
        conoce = False
        conocimientos = None
        cod_tema = -1
        last_msg = tracker.latest_message
        ManipularDatosRegistrados.saveMessageOfInterest(last_msg['metadata'])
        msg_received_id = last_msg['metadata']['message']['message_id']
        print("Tema debate: "+tema_discusion)

        with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async("consult('C:/Users/Usuario/ProyectosRasa/bot_personal_grupal/actions/hechos.pl')", find_all=False)
                    prolog_thread.query_async(f"conoce_acerca_de(Z,X,Y).",find_all=True)
                    sleep(0.1)
                    result = prolog_thread.query_async_result()
                    if result:
                        for p in palabras_clave:
                            for item in result:
                                if p.lower() in str(item['X']).lower():
                                    cod_tema = str(item['Z'])
                                    conoce = True
                                    conocimientos = str(item['Y'])

        if(conoce):
            if(conocimientos != None):
                dispatcher.utter_message(text=conocimientos)
                return [SlotSet('topic_code',cod_tema)]
        else:
            dispatcher.utter_message(text="La verdad, no se sobre el tema")
            url = getInfoAboutTopic(tema_discusion)
            if(url != None):
                dispatcher.utter_message(text="Encontre esto",response_id=msg_received_id)
                dispatcher.utter_message(text=url)
        return []

class ActionGiveOpinion(Action):
    def name(self) -> Text:
       return "action_give_opinion"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:   
        tema_discusion = str(tracker.get_slot("topic_to_discuss"))
        palabras_clave = tema_discusion.split()
        codigo_conoce = str(tracker.get_slot("topic_code"))
        codigo_opinion = str(int(tracker.get_slot("last_opinion_given"))+1)
        
        if(int(codigo_conoce) <= 0):
            dispatcher.utter_message(text="Como ya te dije, no se sobre el tema")
            return []
        else:
            with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async("consult('C:/Users/Usuario/ProyectosRasa/bot_personal_grupal/actions/hechos.pl')", find_all=False)
                    prolog_thread.query_async(f"opina_sobre({codigo_conoce},{codigo_opinion},Z).",find_all=False)
                    sleep(0.1)
                    result = prolog_thread.query_async_result()
                    if(result):
                        if(int(codigo_opinion) <= 1):
                            dispatcher.utter_message(text=f"Pienso que estaria bueno se podria {result[0]['Z']}")
                        else:
                            dispatcher.utter_message(text=f"Tambien creo que {result[0]['Z']}")
                        return [SlotSet('last_opinion_given',str(codigo_opinion))]
        return []

class ActionGiveArgumentForOpinion(Action):
    def name(self) -> Text:
       return "action_give_argument_for_opinion"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tema_discusion = str(tracker.get_slot("topic_to_discuss"))
        codigo_opinion = str(tracker.get_slot("last_opinion_given"))
        codigo_conoce = str(tracker.get_slot("topic_code"))
        
        if(int(codigo_conoce) >= 0):
            with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async("consult('C:/Users/Usuario/ProyectosRasa/bot_personal_grupal/actions/hechos.pl')", find_all=False)
                    prolog_thread.query_async(f"argumento_opinion({codigo_conoce},{codigo_opinion},Z).",find_all=False)
                    sleep(0.1)
                    result = prolog_thread.query_async_result()
                    if(result):
                        dispatcher.utter_message(text=f"Opino esto porque {result[0]['Z']}")

        return []

class ActionSendSupportMessageToUser(Action):
    def name(self) -> Text:
       return "action_send_support_msg_to_user"
    
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msgOfInterest = ManipularDatosRegistrados.getMessageOfInterest()
        if(msgOfInterest != None):
            sendPrivateMessage(msgOfInterest['message']['from']['id'], "Si queres hablar conta conmigo")
        return []

class ActionCheckIfFree(Action):
    def name(self) -> Text:
       return "action_check_if_free"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ManipularDatosRegistrados().resetParticipantsCurrentMeeting()
        last_msg = tracker.latest_message
        ManipularDatosRegistrados.saveMessageOfInterest(last_msg['metadata'])
        msg_received_id = tracker.latest_message['metadata']['message']['message_id']
        dia = tracker.get_slot("weekday")
        hora = tracker.get_slot("hour_of_day")
        turno = tracker.get_slot("time_of_day")
        if(dia == None):
            dia = getCurrentWeekDay()
        else:
            dia = str(dia)
        
        with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async("consult('C:/Users/Usuario/ProyectosRasa/bot_personal_grupal/actions/hechos.pl')", find_all=False)
                    if(hora == None):
                        prolog_thread.query_async(f"actividades_dia({dia},X).",find_all=True)
                        sleep(0.1)
                        result = prolog_thread.query_async_result()
                        if result:
                            max_hr = 0
                            for item in result:
                                if int(item['X']) > max_hr:
                                    max_hr = int(item['X'])
                            dispatcher.utter_message(text="Yo estoy libre a partir de las "+str(max_hr),response_id=msg_received_id)
                            return [SlotSet('hour_of_day',str(max_hr)),SlotSet('free_to_meet',True),FollowupAction('action_ask_that_time_works')]
                        else:
                            dispatcher.utter_message(text="Cuando quieran, yo estoy libre",response_id=msg_received_id)
                            return [SlotSet('free_to_meet',False)]
                    else:
                        if(turno != None):
                            if((str(turno) == "tarde" or str(turno) == "noche") and int(hora) < 12):
                                hora = str(int(hora)+12)
                            else:
                                hora = str(hora)
                        prolog_thread.query_async(f"esta_ocupado({dia},{hora},Y).",find_all=False)
                        sleep(0.1)
                        result = prolog_thread.query_async_result()
                        if(result):
                            dispatcher.utter_message(text="A esa hora yo no puedo, estaria "+str(result[0]['Y']),response_id=msg_received_id)
                            return [SlotSet('free_to_meet',False)]
                        else:
                            dispatcher.utter_message(text="Yo estoy libre",response_id=msg_received_id)
                            return [SlotSet('hour_of_day',str(hora)),SlotSet('free_to_meet',True),FollowupAction('action_ask_that_time_works')]
        return []

class ActionAskThatTimeWorks(Action):
    def name(self) -> Text:
       return "action_ask_that_time_works"
    
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msg_received_id = ManipularDatosRegistrados.getMessageOfInterest()['message']['message_id']
        if(msg_received_id != None):
            dispatcher.utter_message(text="Les convence ese horario?",buttons=[{"title":"Puedo"},{"title":"No puedo"}],
                button_type="reply",response_id=msg_received_id)
        return [FollowupAction('action_listen')]  

def sendPrivateMessage(user_id,msg:str):
    getUrl = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    params = {
        "chat_id" : user_id,
        "text" : msg
    }
    r = requests.get(getUrl,params)

def getChatMemberCount(chat_id):
    getUrl = f'https://api.telegram.org/bot{TOKEN}/getChatMemberCount?chat_id={chat_id}'
    with urlopen(getUrl) as r:
        resp = json.load(r)
    return int(resp['result'])

def pinMessage(chat_id,msg_id):
    getUrl = f'https://api.telegram.org/bot{TOKEN}/pinChatMessage'
    params_ChatMessage = {
        "chat_id" : chat_id,
        "message_id" : msg_id
    }
    r = requests.get(getUrl,params_ChatMessage)

def setNewDescription(chat_id,description):
    getUrl = f'https://api.telegram.org/bot{TOKEN}/setChatDescription'
    params_SetDescription = {
        "chat_id" : chat_id,
        "description" : description
    }
    r = requests.get(getUrl,params_SetDescription)

def sendSticker(chat_id,file_id):
    getUrl = f'https://api.telegram.org/bot{TOKEN}/sendSticker'
    params = {
        "chat_id" : chat_id,
        "sticker" : file_id
    }
    r = requests.get(getUrl,params)
