from __main__ import app
import config

# ------------------ FUNCION POLL ------------------ #

#Encuesta: Guarda los datos de las encuestas que se esten manipulando.
class Poll:
    _code=-1 #Identificador de la encuesta creada.
    _title="Encuesta sin Título" #Título de la encuesta creada.
    _description="--?--" #Descripción de la encuesta creada.
    _state="Por realizar" #Estado de la encuesta 'Por realizar','Abierta','Cerrada'.
    _id_encuestador=0 #Id del encuestador que crea la encuesta. (no implemenado)
    _question=0 #Número de encuestas.
    
    def __init__ (self):
        self._state =-1
        self._state = "Por Realizar"
    
    def setCode(self,code):
        self._code=code

    def setQuestion(self,question):
        self._question=question

    def setTitle(self,title):
        self._title = title
    
    def setDescription(self,description):
        self._description = description
    
    def setState(self,state):
        self._state = state
    
    def getQuestion(self):
        return self._question

    def getTitle(self):
        return self._title
    
    def getCode(self):
        return self._code
    
    def getDescription(self):
        return self._description
   
    def getState(self):
        return self._state 

# Variables Globales
# hace referencia a la ultima encuesta creada
lastPoll = Poll()
app.secret_key = config.SECRET_KEY