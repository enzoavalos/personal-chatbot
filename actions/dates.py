from datetime import datetime

def getCurrentWeekDay(today=None):
    if(today == None):
        today = str(datetime.today().weekday())
    if(today =="0"):
        return "lunes"
    elif (today == "1"):
        return "martes"
    elif (today == "2"):
        return "miercoles"
    elif (today == "3"):
        return "jueves"
    elif (today == "4"):
        return "viernes"
    elif (today == "5"):
        return "sabado"
    elif (today == "6"):
        return "domingo"

def getNextWeekDay():
    today = str(datetime.today().weekday())
    return getCurrentWeekDay(today)

def getCurrentHour():
    return datetime.now().hour