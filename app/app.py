from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_mysqldb import MySQL

app = Flask(__name__)

#CONEXION SQL
app.config['MYSQL_HOST'] = '103.195.100.230'
app.config['MYSQL_USER'] = 'jookeezc_server'
app.config['MYSQL_PASSWORD'] = 'is2_gonzal0'
app.config['MYSQL_DB'] = 'jookeezc_encuesta'
mysql = MySQL(app)

#CONEXION SMTP PARA ENVIO DE CORREOS
app.config['MAIL_SERVER'] = 'encuestas.jookeez.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "no-responder@encuestas.jookeez.com"
app.config['MAIL_PASSWORD'] = "is2_gonzal0"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_MAX_EMAILS'] = 500  # Maximo de correos a enviar
mail = Mail(app)

#VERFICAMOS EL CORREO ELECTRONICO ENVIANDO UN CORREO
@app.route('/enviar-verificacion/', methods=['POST'])
def enviar_verificacion():
    if request.method == 'POST':
        nombre_form = request.form['nombre']
        correo_form = request.form['correo']
        data = {
            'nombre': nombre_form,
            'correo': correo_form
        }
        subject = nombre_form + " necesitamos verificar tu correo"
        enviar_nombre = "SiSoySurvey | Jookeez.com"
        enviar_mail = "no-responder@encuestas.jookeez.com"
        
        mensaje = Message(subject, sender=(enviar_nombre, enviar_mail), recipients=[correo_form])
        mensaje.html = render_template("mail-verificar.html", data=data)
        mail.send(mensaje)
        informacion = {
            'titulo_favicon': "Verificación de correo electrónico",
            'titulo': "¡Revisa tu correo!",
            'descripcion': "Te enviamos una confirmación a tu correo electrónico.",
            'texto_boton': "Ir al HOME",
            'enlace_boton': "https://encuestas.jookeez.com"
        }
        return render_template("aviso-boton.html", informacion=informacion)

#EL USUARIO HA CONFIRMADO SU CORREO, ESTA ES LA RESPUESTA 
@app.route('/confirmacion/<nombre>/<correo>')
def confirmacion(nombre, correo):

    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO Encuestados (correo,nombre) VALUES (%s,%s)',(correo,nombre))
    mysql.connection.commit()

    informacion = {
        'titulo_favicon': "Cuenta verificada!",
        'titulo': "¡" + nombre + ", eres oficialmente bienvenido!",
        'descripcion': "Tu correo " + correo + " ha sido verificado exitosamente.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso-boton.html", informacion=informacion)

#ENVIA ENCUESTAS POR CORREO A LOS PARTICIPANTES
@app.route('/enviar-mensaje/<nombre>/<correo>/<int:id_encuesta>/<encuesta>')
def enviar_mensaje(nombre, correo, id_encuesta, encuesta):
    data = {
        'nombre': nombre,
        'correo': correo,
        'id_encuesta': id_encuesta,
        'encuesta': encuesta
    }
    subject = encuesta + " ya está disponible!"
    enviar_nombre = "SiSoySurvey | Jookeez.com"
    enviar_mail = "no-responder@encuestas.jookeez.com"
    
    mensaje = Message(subject, sender=(enviar_nombre, enviar_mail), recipients=[correo])
    mensaje.html = render_template("mail.html", data=data)
    mail.send(mensaje)
    informacion = {
        'titulo_favicon': "Envío de encuestas",
        'titulo': "¡Encuesta enviada!",
        'descripcion': "En unos momentos el encuestado la recibirá en su correo electrónico.",
        'texto_boton': "Volver",
        'enlace_boton': "javascript:history.back()"
    }
    return render_template("aviso-boton.html", informacion=informacion)

#EL USUARIO SE DA DE BAJA Y SE CONFIRMA SU DESUSCRIPCION
@app.route('/desuscribir/<correo>')
def desuscribir(correo):
    informacion = {
        'titulo_favicon': "Darse de baja",
        'titulo': "¡Lamentamos que te vayas!",
        'descripcion': "El correo " + correo + " fue dado de baja exitosamente.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Encuestados WHERE correo = %s', [correo])
    mysql.connection.commit()

    return render_template("aviso-boton.html", informacion=informacion)

#VERFICAMOS EL CORREO ELECTRONICO ENVIANDO UN CORREO
@app.route('/enviar-verificacion-encuestador/', methods=['POST'])
def enviar_verificacion_portal():
    if request.method == 'POST':
        nombre_form = request.form['nombre']
        correo_form = request.form['correo']
        data = {
            'nombre': nombre_form,
            'correo': correo_form
        }
        subject = nombre_form + " necesitamos verificar tu correo"
        enviar_nombre = "SiSoySurvey | Jookeez.com"
        enviar_mail = "no-responder@encuestas.jookeez.com"
        
        mensaje = Message(subject, sender=(enviar_nombre, enviar_mail), recipients=[correo_form])
        mensaje.html = render_template("mail-verificar.html", data=data)
        mail.send(mensaje)
        return redirect(url_for('portal_encuestador_participantes_agregar'))

#MUESTA EL LISTADO DE PARTICIPANTES EN EL PORTAL DEL ENCUESTADOR
@app.route('/portal-encuestador-participantes-listado')
def portal_encuestador_participantes_listado():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados')
    data = cur.fetchall()
    return render_template("portal-encuestador-participantes-listado.html", encuestados = data)

#EL ENCUESTADOR ELIMINA AL PARTICIPANTE DE LA BASE DE DATOS
@app.route('/eliminar-participante/<correo>')
def eliminar_participante(correo):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Encuestados WHERE correo = %s', [correo])
    mysql.connection.commit()
    return redirect(url_for('portal_encuestador_participantes'))


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

#Variables Globales
# hace referencia a la ultima encuesta creada
lastPoll = Poll()
app.secret_key = "mysecretkey"


# MUESTRA EL LISTADO DE ENCUESTAS POR REALIZAR
@app.route('/portal-encuestador-encuestas-realizar')
def portal_encuestador_encuestas_realizar():
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Por realizar'")
    Ready = cur1.fetchall()
    return render_template("portal-encuestador-encuestas-realizar.html", pollsReady=Ready)

# MUESTRA EL LISTADO DE ENCUESTAS ABIERTAS
@app.route('/portal-encuestador-encuestas-abiertas')
def portal_encuestador_encuestas_abiertas():
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Abierta'")
    Open = cur2.fetchall()
    return render_template("portal-encuestador-encuestas-abiertas.html", pollsOpen=Open)

# MUESTRA EL LISTADO DE ENCUESTAS FINALIZADAS
@app.route('/portal-encuestador-encuestas-finalizadas')
def portal_encuestador_encuestas_finalizadas():
    cur3 = mysql.connection.cursor()
    cur3.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Cerrada'" )
    Closed = cur3.fetchall()
    return render_template("portal-encuestador-encuestas-finalizadas.html", pollsClosed=Closed)



#VEMOS EN EL PORTAL PRIVADO DEL PARTICIPANTE EL LISTADO DE ENCUESTAS QUE PUEDE RESPONDER
#Ingreso mail, del mail que me de el id_encuesta
@app.route("/portal-participante-encuestas-responder/<mail>")
def encuestas_encuestado(mail):
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT Enc.id_encuesta,Enc.nombre,Enc.descripcion, Enc.estado,Enc.preguntas  FROM(   SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Por realizar') as Enc ,(SELECT r.id_encuesta FROM Responde as r WHERE r.correo = %s ) as Res WHERE Res.id_encuesta=Enc.id_encuesta ",[mail])
    data = cur1.fetchall()
    return render_template("portal-participante-encuestas-responder.html", data=data)


#VEMOS EN EL PORTAL PRIVADO DEL PARTICIPANTE EL LISTADO DE ENCUESTAS QUE RESPONDIÓ
@app.route('/portal-participante-encuestas-respondidas/<mail>')
def encuestas_respondidas_participante(mail):
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT Enc.id_encuesta,Enc.nombre,Enc.descripcion, Enc.estado,Enc.preguntas  FROM(   SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Cerrada') as Enc ,(SELECT r.id_encuesta FROM Responde as r WHERE r.correo = %s ) as Res WHERE Res.id_encuesta=Enc.id_encuesta ",[mail])
    data = cur1.fetchall()
    return render_template("portal-participante-encuestas-respondidas.html", data=data)

#PODEMOS VER LAS ULTIMAS ENCUESTAS QUE ESTAN ABIERTAS
@app.route('/ultimas-encuestas')
def ultimas_encuestas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_encuesta, nombre, descripcion, fecha_inicio, fecha_fin, preguntas FROM Encuestas WHERE estado='Abierta'")
    data = cur.fetchall()
    return render_template("ultimas-encuestas.html", data=data)

#PODEMOS VER LAS ULTIMAS ENCUESTAS QUE ESTAN ABIERTAS EN EL INDEX
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_encuesta, nombre, descripcion FROM Encuestas WHERE estado='Abierta' LIMIT 3")
    data = cur.fetchall()
    return render_template("index.html", data=data)
    
#VERIFICA EL INICIO DE SESION DEL ENCUESTADOR
@app.route("/logear", methods = ['GET','POST'])
def logear():
    if request.method =='POST':
        email = request.form['usuario']
        password = request.form['contraseña']
        a = "@encuestas.jookeez.com"
        email = email+a
        #print(email)
        #print(password)
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Encuestadores WHERE correo = %s', [email])
        user = cur.fetchone()
        cur.close()
        #print(user[2])

        if user is not None:
            if password == user[2]:
                session['name'] = user[1] #Se le pasa el nombre al HTML del portal
                return redirect(url_for('portal_encuestador'))
            else: 
                return "correo y/o contraseña no valido" #Error en correo escrito o contraseña
        else:
            return "Correo no registrado"        
        cur.close()       
        #if len(user)>0:
        #return "Bienvenido :)"
        #else:
        #    return "Error, Correo y/o contraseña no valida"


    return redirect(url_for('iniciar_sesion_encuestador'))        

#VERIFICA EL INICIO DE SESION DEL ENCUESTADOR
@app.route("/logear-participante", methods = ['GET','POST'])
def logear_participante():
    if request.method =='POST':
        email = request.form['correo']
        #print(email)
        #print(password)
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Encuestados WHERE correo = %s', [email])
        user = cur.fetchone()
        cur.close()
        #print(user[2])

        if user is not None:
            if email == user[0]:
                session['name'] = user[1] #Se le pasa el nombre al HTML del portal
                return redirect(url_for('portal_participante'))
            else: 
                return "correo no valido" #Error en correo escrito o contraseña
        else:
            return "Correo no registrado"
        cur.close()       
        #if len(user)>0:
        #return "Bienvenido :)"
        #else:
        #    return "Error, Correo y/o contraseña no valida"

    return redirect(url_for('iniciar_sesion'))  








#PAGINAS QUE SOLO RETORNAN UN ARCHIVO HTML
@app.route('/sprint1')
def sprint1():
    return render_template("sprint1.html")

@app.route('/sprint2')
def sprint2():
    return render_template("sprint2.html")

@app.route('/iniciar-sesion')
def iniciar_sesion():
    return render_template("iniciar-sesion.html")

@app.route('/iniciar-sesion-encuestador')
def iniciar_sesion_encuestador():
    return render_template("iniciar-sesion-encuestador.html")

@app.route('/registrarse')
def registrarse():
    return render_template("registrarse.html")

@app.route('/registrarse-encuestador')
def registrarse_encuestador():
    return render_template("registrarse-encuestador.html")

@app.route('/conocenos')
def conocenos():
    return render_template("conocenos.html")

@app.route('/terminos')
def terminos():
    return render_template("terminos.html")

@app.route('/portal-participante')
def portal_participante():
    return render_template("portal-participante.html")

@app.route('/portal-participante-encuestas-responder')
def portal_participante_encuestas_responder():
    return render_template("portal-participante-encuestas-responder.html")

@app.route('/portal-participante-encuestas-respondidas')
def portal_participante_encuestas_respondidas():
    return render_template("portal-participante-encuestas-respondidas.html")

@app.route('/portal-participante-perfil')
def portal_participante_perfil():
    return render_template("portal-participante-perfil.html")

@app.route('/portal-participante-ajustes')
def portal_participante_ajustes():
    return render_template("portal-participante-ajustes.html")

@app.route('/portal-encuestador')
def portal_encuestador():
    return render_template("portal-encuestador.html")

@app.route('/portal-encuestador-participantes-agregar')
def portal_encuestador_participantes_agregar():
    return render_template("portal-encuestador-participantes-agregar.html")

@app.route('/portal-encuestador-encuestas-crear')
def portal_encuestador_encuestas_crear():
    return render_template("portal-encuestador-encuestas-crear.html")

@app.route('/portal-encuestador-resultados')
def portal_encuestador_resultados():
    return render_template("portal-encuestador-resultados.html")

@app.route('/portal-encuestador-estadisticas')
def portal_encuestador_estadisticas():
    return render_template("portal-encuestador-estadisticas.html")

@app.route('/portal-encuestador-perfil')
def portal_encuestador_perfil():
    return render_template("portal-encuestador-perfil.html")

@app.route('/portal-encuestador-ajustes')
def portal_encuestador_ajustes():
    return render_template("portal-encuestador-ajustes.html")




# ------------------ MANEJO DE ERRORES ------------------ #

#MUESTRA LOS ERRORES CORRECTAMENTE
@app.errorhandler(400)
def error_400(error):
    informacion = {
        'titulo_favicon': "Error 400",
        'titulo': "¡Se nos cayó un tornillo!",
        'descripcion': "Estamos presentando inestabilidad en el servicio.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso-boton.html", informacion=informacion), 400

@app.errorhandler(401)
def error_401(error):
    informacion = {
        'titulo_favicon': "Error 401",
        'titulo': "¡Necesitas autenticarte!",
        'descripcion': "Estas tratando de entrar a una página sin credenciales.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso-boton.html", informacion=informacion), 401

@app.errorhandler(403)
def error_403(error):
    informacion = {
        'titulo_favicon': "Error 403",
        'titulo': "¡Alerta de intruso!",
        'descripcion': "Estas tratando de entrar a una página sin autorización.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso-boton.html", informacion=informacion), 403

@app.errorhandler(404)
def error_404(error):
    informacion = {
        'titulo_favicon': "Error 404",
        'titulo': "¡Houston, tenemos un problema!",
        'descripcion': "La página que estas buscando no existe o no está disponible por el momento.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso-boton.html", informacion=informacion), 404

@app.errorhandler(408)
def error_408(error):
    informacion = {
        'titulo_favicon': "Error 408",
        'titulo': "¡Se nos quedó una letra en el camino!",
        'descripcion': "No pudimos recibir toda la información por completo. Intenta actualizar la página.",
        'texto_boton': "Actualizar página",
        'enlace_boton': "javascript:location.reload()"
    }
    return render_template("aviso-boton.html", informacion=informacion), 408

@app.errorhandler(410)
def error_410(error):
    informacion = {
        'titulo_favicon': "Error 410",
        'titulo': "¡Botamos la basura!",
        'descripcion': "La página que estas buscando fue eliminada.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso-boton.html", informacion=informacion), 410

@app.errorhandler(500)
def error_500(error):
    informacion = {
        'titulo_favicon': "Error 500",
        'titulo': "¡Se cayó el sistema!",
        'descripcion': "Estamos teniendo problemas internos. ¡Volveremos pronto!",
    }
    return render_template("aviso.html", informacion=informacion), 500

@app.errorhandler(503)
def error_503(error):
    informacion = {
        'titulo_favicon': "Error 503",
        'titulo': "¡Se cayó el sistema!",
        'descripcion': "Nuestro servidor no esta disponible en este momento.",
    }

    return render_template("aviso.html", informacion=informacion), 503




#SIN ESTO NO VIVIMOS
if __name__ == '__main__':
    app.register_error_handler(400, error_400)
    app.register_error_handler(401, error_401)
    app.register_error_handler(403, error_403)
    app.register_error_handler(404, error_404)
    app.register_error_handler(408, error_408)
    app.register_error_handler(410, error_410)
    app.register_error_handler(500, error_500)
    app.run(debug=True)
