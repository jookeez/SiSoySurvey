from flask import render_template, request
from flask_mail import Mail, Message
from __main__ import app
from src.bd import mysql
from src.funciones import procesar_texto
import config

# ------------------ CORREO ELECTRONICO ------------------ #

# CONEXION SMTP PARA ENVIO DE CORREOS
app.config['MAIL_SERVER'] = config.SMTP_SERVER
app.config['MAIL_PORT'] = config.SMTP_PORT
app.config['MAIL_USERNAME'] = config.SMTP_USER
app.config['MAIL_PASSWORD'] = config.BD_PASSWD
app.config['MAIL_USE_TLS'] = config.SMTP_TLS
app.config['MAIL_USE_SSL'] = config.SMTP_SSL
app.config['MAIL_MAX_EMAILS'] = config.SMTP_MAX_MAILS  # Maximo de correos a enviar
mail = Mail(app)

# VERFICAMOS EL CORREO ELECTRONICO ENVIANDO UN CORREO
@app.route('/enviar-verificacion/', methods=['POST'])
def enviar_verificacion():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo_form = request.form['correo']
        nombre_form = procesar_texto(nombre)
        data = {
            'nombre': nombre_form,
            'correo': correo_form
        }
        subject = nombre_form + " necesitamos verificar tu correo"
        enviar_nombre = "SiSoySurvey | Jookeez.com"
        enviar_mail = "no-responder@encuestas.jookeez.com"
        
        mensaje = Message(subject, sender=(enviar_nombre, enviar_mail), recipients=[correo_form])
        mensaje.html = render_template("correo/verificar.html", data=data)
        mail.send(mensaje)
        informacion = {
            'titulo_favicon': "Verificación de correo electrónico",
            'titulo': "¡Revisa tu correo!",
            'descripcion': "Te enviamos una confirmación a " + correo_form
        }
        return render_template("aviso/simple.html", informacion=informacion)

# EL USUARIO HA CONFIRMADO SU CORREO, ESTA ES LA RESPUESTA 
@app.route('/confirmacion/<nombre>/<correo>')
def confirmacion(nombre, correo):
    nombre_procesado = procesar_texto(nombre)
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO Encuestados (correo,nombre) VALUES (%s,%s)',[correo, nombre_procesado])
    mysql.connection.commit()

    informacion = {
        'titulo_favicon': "Cuenta verificada!",
        'titulo': "¡" + nombre_procesado + ", eres oficialmente bienvenido!",
        'descripcion': "Tu correo " + correo + " ha sido verificado exitosamente.",
        'texto_boton': "Iniciar Sesión",
        'enlace_boton': "/iniciar-sesion"
    }
    return render_template("aviso/boton.html", informacion=informacion)

#ENVIAR ENCUESTAS POR CORREO A TODOS LOS PARTICIPANTES
@app.route('/enviar-encuesta/<int:id_encuesta>')
def enviar_encuesta(id_encuesta):
    query="UPDATE Encuestas SET estado='Abierta',fecha_inicio=NOW() WHERE id_encuesta ="+str(id_encuesta)
    cur = mysql.connection.cursor()
    cur.execute(query)
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT e.nombre , e.correo FROM Encuestados as e')
    data = cur.fetchall()
    curr = mysql.connection.cursor()
    curr.execute('SELECT en.nombre FROM Encuestas as en WHERE id_encuesta = %s',[id_encuesta])
    name_encuesta = curr.fetchone()

    for row in data:
        enviar_mensaje(row[0],row[1],id_encuesta,name_encuesta[0])

    informacion = {
        'titulo_favicon': "Envío de encuestas",
        'titulo': "¡Encuestas enviadas!",
        'descripcion': "En unos momentos los participantes la recibirán en sus correos electrónicos.",
        'texto_boton': "Volver",
        'enlace_boton': "javascript:history.back()"
    }
    mysql.connection.commit()
    return render_template("aviso/boton.html", informacion=informacion)

# ENVIA ENCUESTAS POR CORREO A LOS PARTICIPANTES
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
    mensaje.html = render_template("correo/mail.html", data=data)
    mail.send(mensaje)
    return 1
