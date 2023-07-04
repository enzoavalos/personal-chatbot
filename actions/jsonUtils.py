import os.path
import json

class OperarArchivo():
    @staticmethod
    def guardar(AGuardar):
        with open(".\\actions\\datos","w") as archivo_descarga:
            json.dump(AGuardar, archivo_descarga, indent=4)
        archivo_descarga.close()

    @staticmethod
    def cargarArchivo(): 
        if os.path.isfile(".\\actions\\datos"):
            with open(".\\actions\\datos","r") as archivo_carga:
                retorno=json.load(archivo_carga)
                archivo_carga.close()
        else:
            retorno={}
        return retorno

class ManipularDatosRegistrados():
    @staticmethod
    def getMeetingsList():
        datos = OperarArchivo.cargarArchivo()
        if not datos['meetings']:
            return None
        else:
            return datos['meetings']

    @staticmethod
    def checkDateIsFree(dia,hora)->bool:
        datos = OperarArchivo.cargarArchivo()
        if not dia in datos['meetings']:
            return True
        else:
            for i in range(int(hora)-3,int(hora)+3):
                if str(i) == datos['meetings'][dia]['time']:
                    return False
            return True

    @staticmethod
    def resetParticipantsCurrentMeeting():
        datos = OperarArchivo.cargarArchivo()
        datos['meeting_scheduling']['participants'] = 0
        OperarArchivo().guardar(datos)

    @staticmethod
    def increaseParticipants():
        datos = OperarArchivo.cargarArchivo()
        amount = int(datos['meeting_scheduling']['participants'])
        datos['meeting_scheduling']['participants'] = amount+1
        OperarArchivo().guardar(datos)

    @staticmethod
    def getCurrentAmountRegistered():
        datos = OperarArchivo.cargarArchivo()
        return int(datos['meeting_scheduling']['participants'])

    @staticmethod
    def getMessageOfInterest():
        datos = OperarArchivo.cargarArchivo()
        return datos['msg_of_interest']

    @staticmethod
    def saveMeeting(dia,hora):
        datos = OperarArchivo.cargarArchivo()
        if not dia in datos['meetings']:
            datos['meetings'][dia] = {}
        datos['meetings'][dia]['time'] = hora
        OperarArchivo.guardar(datos)

    @staticmethod
    def saveMessageOfInterest(msgToSave):
        datos = OperarArchivo.cargarArchivo()
        datos['msg_of_interest'] = msgToSave
        OperarArchivo.guardar(datos)