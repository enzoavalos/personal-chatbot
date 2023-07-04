import pyjokes

def getGeekJoke():
    return pyjokes.get_joke(language='es',category='neutral')