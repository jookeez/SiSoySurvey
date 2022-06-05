#Encuesta: Guarda los datos de las encuestas que se esten manipulando.
class Poll:

    _code=-1 #Identificador de la encuesta creada.
    _title="Encuesta sin Título" #Título de la encuesta creada.
    _description="--?--" #Descripción de la encuesta creada.
    _state="Por realizar" #Estado de la encuesta 'Por realizar','Abierta','Cerrada'.
    _id_encuestador=0 #Id del encuestador que crea la encuesta. (no implemenado)
    _question=0 #Número de encuestas.
    
    def __init__ (self): #Constructor de la clase Poll
        self._state =-1
        self._state = "Por Realizar"
    
    def setCode(self,code):#seter del atributo code
        self._code=code

    def setQuestion(self,question): #seter del atributo question
        self._question=question

    def setTitle(self,title): #seter del atributo title
        self._title = title
    
    def setDescription(self,description):#seter del atributo description
        self._description = description
    
    def setState(self,state):#seter del atributo state
        self._state = state
    
    def getQuestion(self): #geter del atributo question
        return self._question

    def getTitle(self): #geter del atributo title
        return self._title
    
    def getCode(self): #geter del atributo code
        return self._code
    
    def getDescription(self):#geter del atributo description
        return self._description
   
    def getState(self):#geter del atributo state
        return self._state       