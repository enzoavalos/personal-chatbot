import wikipedia

def getInfoAboutTopic(topic:str):
    wikipedia.set_lang("es")
    try:
        topic_info = wikipedia.page(topic)
        return topic_info.url
    except:
        return None