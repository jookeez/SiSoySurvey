from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from datetime import date, datetime

app = Flask(__name__)

# CONEXION SQL
app.config['MYSQL_HOST'] = '103.195.100.230'
app.config['MYSQL_USER'] = 'jookeezc_server'
app.config['MYSQL_PASSWORD'] = 'is2_gonzal0'
app.config['MYSQL_DB'] = 'jookeezc_encuesta'
mysql = MySQL(app)

'''
{% if 'participante' in session %}
{% elif 'encuestador' in session %}
{% else %}
{% endif %}
'''

# ------------------ CORREO ELECTRONICO ------------------ #

# CONEXION SMTP PARA ENVIO DE CORREOS
app.config['MAIL_SERVER'] = 'encuestas.jookeez.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "no-responder@encuestas.jookeez.com"
app.config['MAIL_PASSWORD'] = "is2_gonzal0"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_MAX_EMAILS'] = 500  # Maximo de correos a enviar
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
        mensaje.html = render_template("mail-verificar.html", data=data)
        mail.send(mensaje)
        informacion = {
            'titulo_favicon': "Verificación de correo electrónico",
            'titulo': "¡Revisa tu correo!",
            'descripcion': "Te enviamos una confirmación a " + correo_form
        }
        return render_template("aviso.html", informacion=informacion)

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
    return render_template("aviso-boton.html", informacion=informacion)

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
    return render_template("aviso-boton.html", informacion=informacion)

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
    mensaje.html = render_template("mail.html", data=data)
    mail.send(mensaje)
    return 1




# ------------------ ENCUESTADOR ------------------ #

#PORTAL DEL ENCUESTADOR
@app.route('/portal-encuestador')
def portal_encuestador():
    cur = mysql.connection.cursor()

    #TOTAL DE PARTICIPANTES DEL LISTADO
    cur.execute('SELECT COUNT(*) FROM Encuestados')
    data_participantes = cur.fetchone()

    #PRIMERA ENCUESTA ABIERTA
    cur.execute('SELECT id_encuesta, nombre FROM Encuestas WHERE estado = "Abierta" ORDER BY id_encuesta ASC LIMIT 1')
    data_enc_abierta_asc_1 = cur.fetchone()

    #PARTICIPANTES QUE RESPONDIERON LA PRIMERA ENCUESTA ABIERTA
    cur.execute('SELECT COUNT(*) FROM Responde WHERE id_encuesta = %s', [data_enc_abierta_asc_1[0]])
    data_count_enc_abierta_asc_1 = cur.fetchone()

    #ULTIMA ENCUESTA ABIERTA
    cur.execute('SELECT id_encuesta, nombre, fecha_fin FROM Encuestas WHERE estado = "Abierta" ORDER BY id_encuesta DESC LIMIT 1')
    data_enc_abierta_desc_1 = cur.fetchone()
    
    #CANTIDAD DE ENCUESTAS CERRADAS
    cur.execute('SELECT COUNT(*) FROM Encuestas WHERE Estado = "Cerrada"')
    data_encuestas = cur.fetchone()

    #DATOS DE LA ULTIMA ENCUESTA FINALIZADA
    cur.execute('SELECT id_encuesta, nombre, fecha_inicio, fecha_fin FROM Encuestas WHERE estado = "Cerrada" ORDER BY id_encuesta DESC LIMIT 1')
    data_ue = cur.fetchone()

    #PARTICIPANTES QUE RESPONDIERON LA ULTIMA ENCUESTA FINALIZADA
    cur.execute('SELECT COUNT(*) FROM Responde WHERE id_encuesta = %s', [data_ue[0]])
    data_count = cur.fetchone()

    informacion = {
        'cont_participantes': data_participantes[0],
        'enc_abierta_asc_1_nombre': data_enc_abierta_asc_1[1],
        'cont_enc_abierta_asc_1': data_count_enc_abierta_asc_1[0],
        'enc_abierta_desc_1_nombre': data_enc_abierta_desc_1[1],
        'enc_abierta_desc_1_dias': diferenciaDias(data_enc_abierta_desc_1[2]),
        'enc_abierta_desc_1_dias_neg': diferenciaNegativaDias(data_enc_abierta_desc_1[2]),
        'cont_encuestas_fin': data_encuestas[0],
        'ue_id': data_ue[0],
        'ue_nombre': data_ue[1],
        'ue_fecha_inicio': data_ue[2],
        'ue_fecha_fin': data_ue[3],
        'ue_fecha_finaliza': diferenciaNegativaDias(data_ue[3]),
        'ue_participantes': data_count[0]
    }
    return render_template("portal-encuestador.html", informacion=informacion)

# AGREGAMOS UN NUEVO ENCUESTADOR A LA BASE DE DATOS
@app.route('/agregar-encuestador/', methods=['POST'])
def agregar_encuestador():
    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario = request.form['usuario']
        password = request.form['password']
        password_repetir = request.form['password_repetir']
        palabra_clave = request.form['palabra_clave']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Encuestadores WHERE correo = %s', [usuario])
        usuario_existe = cur.fetchone()
        cur.execute('SELECT * FROM PalabraClave WHERE palabra_clave = %s', [palabra_clave])
        clave = cur.fetchone()
        cur.close()

        if usuario != usuario_existe and password == password_repetir and clave[0] == palabra_clave:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO Encuestadores (nombre, contraseña, correo) VALUES (%s,%s,%s)', [nombre, password, usuario])
            mysql.connection.commit()

            informacion = {
                'titulo_favicon': "Cuenta creada!",
                'titulo': "¡" + nombre + ", eres oficialmente un encuestador!",
                'descripcion': "Tu cuenta ha sido creada exitosamente.",
                'texto_boton': "Iniciar Sesión",
                'enlace_boton': "/iniciar-sesion-encuestador"
            }
            return render_template("aviso-boton.html", informacion=informacion)

# CUANDO AGREGAMOS UN NUEVO PARTICIPANTE EN EL PORTAL, 
# VERFICAMOS EL CORREO ELECTRONICO ENVIANDO UN CORREO
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

# MUESTRA EL LISTADO DE PARTICIPANTES EN EL PORTAL DEL ENCUESTADOR
@app.route('/portal-encuestador-participantes-listado')
def portal_encuestador_participantes_listado():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados')
    data = cur.fetchall()
    return render_template("portal-encuestador-participantes-listado.html", encuestados=data)

# MUESTRA EL LISTADO DE ENCUESTAS POR REALIZAR
@app.route('/portal-encuestador-encuestas-realizar')
def portal_encuestador_encuestas_realizar():
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Por realizar'")
    Ready = cur1.fetchall()
    return render_template("portal-encuestador-encuestas-realizar.html", Ready=Ready)

# MUESTRA EL LISTADO DE ENCUESTAS ABIERTAS
@app.route('/portal-encuestador-encuestas-abiertas')
def portal_encuestador_encuestas_abiertas():
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Abierta'")
    Open = cur2.fetchall()
    return render_template("portal-encuestador-encuestas-abiertas.html", Open=Open)

# MUESTRA EL LISTADO DE ENCUESTAS FINALIZADAS
@app.route('/portal-encuestador-encuestas-finalizadas')
def portal_encuestador_encuestas_finalizadas():
    cur3 = mysql.connection.cursor()
    cur3.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Cerrada'" )
    Closed = cur3.fetchall()
    return render_template("portal-encuestador-encuestas-finalizadas.html", Closed=Closed)

# EL ENCUESTADOR CAMBIA SU NOMBRE EN EL PORTAL
@app.route("/cambiar-nombre-encuestador/<correo>", methods=['POST'])
def cambiar_nombre_encuestador(correo):
    if request.method =='POST':
        nuevo_nombre = request.form['nuevo_nombre']
        cur = mysql.connection.cursor()
        cur.execute('UPDATE Encuestadores SET nombre = %s WHERE correo = %s',[nuevo_nombre, correo])
        mysql.connection.commit()
        session['nombre'] = nuevo_nombre
        return redirect(url_for('portal_encuestador_perfil'))

# EL ENCUESTADOR CAMBIA SU CONTRASEÑA EN EL PORTAL
@app.route("/cambiar-password-encuestador/<correo>", methods=['POST'])
def cambiar_password_encuestador(correo):
    if request.method =='POST':
        password = request.form['password']
        password_repetir = request.form['password_repetir']
        if password == password_repetir:
            cur = mysql.connection.cursor()
            cur.execute('UPDATE Encuestadores SET contraseña = %s WHERE correo = %s',[password, correo])
            mysql.connection.commit()
            return redirect(url_for('portal_encuestador_perfil'))
        else:
            # AGREGAR MENSAJE DE CONTRASEÑAS NO SON IGUALES
            return redirect(url_for('portal_encuestador_perfil'))

# EL USUARIO SE DA DE BAJA Y SE CONFIRMA SU DESUSCRIPCION
@app.route('/dar-de-baja-encuestador/<correo>', methods=['POST'])
def dar_de_baja_encuestador(correo):
    if request.method =='POST':
        palabra_clave = request.form['palabra_clave']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM PalabraClave WHERE palabra_clave = %s', [palabra_clave])
        mysql.connection.commit()
        clave = cur.fetchone()
        cur.close()

        if clave[0] == palabra_clave:
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM Encuestadores WHERE correo = %s', [correo])
            mysql.connection.commit()
            informacion = {
                'titulo_favicon': "Eliminar mi cuenta",
                'titulo': "¡Fue un gusto trabajar contigo!",
                'descripcion': "El correo " + correo + "@encuestas.jookeez.com fue eliminado exitosamente."
            }
            return render_template("aviso.html", informacion=informacion)
        else:
            # ENVIAR MENSAJE AL USUARIO
            return redirect(url_for('portal_encuestador_perfil'))
    else:
        return redirect(url_for('portal_encuestador_perfil'))

#El usuario puede visualizar la información de la encuesta
@app.route("/portal-encuestador-encuestas-visualizar/<id_encuesta>") 
def visualizar_encuesta(id_encuesta):
    cur = mysql.connection.cursor()
    cur.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.id_encuesta=%s",[id_encuesta])
    polls = cur.fetchall()

    cur.execute("SELECT P.id_pregunta, P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
    questions=cur.fetchall()

    cur.execute("SELECT A.id_alternativa,A.descripcion  FROM Alternativas as A,Preguntas as P,Encuestas as E  WHERE E.id_encuesta=%s AND P.id_encuesta=E.id_encuesta AND P.id_pregunta=A.id_pregunta",[id_encuesta])
    options=cur.fetchall()

    return render_template("portal-encuestador-encuestas-visualizar.html"
    ,polls=polls
    ,questions=questions
    ,options=options
    ,id_encuesta=id_encuesta)


@app.route("/portal-encuestador-visualizar-resultados/<id_encuesta>") 
def visualizar_resultados(id_encuesta):
    cur = mysql.connection.cursor()
    cur.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.id_encuesta=%s",[id_encuesta])
    polls = cur.fetchall()

    cur.execute("SELECT P.id_pregunta, P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
    questions=cur.fetchall()

    cur.execute("SELECT A.id_alternativa,A.descripcion  FROM Alternativas as A,Preguntas as P,Encuestas as E  WHERE E.id_encuesta=%s AND P.id_encuesta=E.id_encuesta AND P.id_pregunta=A.id_pregunta",[id_encuesta])
    options=cur.fetchall()

    values = []

    for f in options:
        values.append(resultados_alternativa(f[0]))

    return render_template("portal-encuestador-visualizar-resultados.html"
    ,polls=polls
    ,questions=questions
    ,options=options
    ,id_encuesta=id_encuesta,
    values=values)

#El usuario accede al portal de creacion de encuestas
@app.route("/portal-encuestador-encuestas-crear/<int:question_number>")
def nueva_encuesta(question_number):
    return render_template("portal-encuestador-encuestas-crear.html",question_number=question_number)
    
#El usuario puede editar toda la informacion de la encuesta 
@app.route("/portal-encuestador-encuestas-editar/<id_encuesta>") 
def editar_encuesta(id_encuesta):
    cur = mysql.connection.cursor()
    cur.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.id_encuesta=%s",[id_encuesta])
    polls = cur.fetchall()

    cur.execute("SELECT P.id_pregunta, P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
    questions=cur.fetchall()

    cur.execute("SELECT A.id_alternativa,A.descripcion  FROM Alternativas as A,Preguntas as P,Encuestas as E  WHERE E.id_encuesta=%s AND P.id_encuesta=E.id_encuesta AND P.id_pregunta=A.id_pregunta",[id_encuesta])
    options=cur.fetchall()

    return render_template("portal-encuestador-encuestas-editar.html"
    ,polls=polls
    ,questions=questions
    ,options=options
    ,id_encuesta=id_encuesta)




# ------------------ PARTICIPANTE ------------------ #

@app.route('/portal-participante')
def portal_participante():
    cur = mysql.connection.cursor()

    #CANTIDAD DE ENCUESTAS QUE HA RESPONDIDO
    cur.execute('SELECT COUNT(*) FROM Responde WHERE correo = %s', [session['correo']])
    data_count_encuestas_resp = cur.fetchone()

    informacion = {
        'encuestas_respondidas': data_count_encuestas_resp[0]
    }

    return render_template("portal-participante.html", informacion=informacion)

# VEMOS EN EL PORTAL PRIVADO DEL PARTICIPANTE EL LISTADO DE ENCUESTAS QUE PUEDE RESPONDER
@app.route("/portal-participante-encuestas-responder/<mail>")
def encuestas_encuestado(mail):
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT Enc.id_encuesta,Enc.nombre,Enc.descripcion, Enc.estado,Enc.preguntas  FROM(   SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Abierta') as Enc ,(SELECT r.id_encuesta FROM Responde as r WHERE r.correo = %s ) as Res WHERE Res.id_encuesta=Enc.id_encuesta ",[mail])
    data = cur1.fetchall()
    return render_template("portal-participante-encuestas-responder.html", data=data,mail=mail)

# VEMOS EN EL PORTAL PRIVADO DEL PARTICIPANTE EL LISTADO DE ENCUESTAS QUE YA RESPONDIÓ
@app.route('/portal-participante-encuestas-respondidas/<mail>')
def encuestas_respondidas_participante(mail):
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT Enc.id_encuesta,Enc.nombre,Enc.descripcion, Enc.estado,Enc.preguntas  FROM(   SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Cerrada') as Enc ,(SELECT r.id_encuesta FROM Responde as r WHERE r.correo = %s ) as Res WHERE Res.id_encuesta=Enc.id_encuesta ",[mail])
    data = cur1.fetchall()
    return render_template("portal-participante-encuestas-respondidas.html", data=data)

# EL PARTICIPANTE CAMBIA SU NOMBRE EN EL PORTAL
@app.route("/cambiar-nombre-participante/<correo>", methods=['POST'])
def cambiar_nombre_participante(correo):
    if request.method =='POST':
        nuevo_nombre = request.form['nuevo_nombre']
        cur = mysql.connection.cursor()
        cur.execute('UPDATE Encuestados SET nombre = %s WHERE correo = %s',[nuevo_nombre, correo])
        mysql.connection.commit()
        session['nombre'] = nuevo_nombre
        return redirect(url_for('portal_participante_perfil'))

# EL ENCUESTADOR ELIMINA AL PARTICIPANTE DE LA BASE DE DATOS
@app.route('/eliminar-participante/<correo>')
def eliminar_participante(correo):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Encuestados WHERE correo = %s', [correo])
    mysql.connection.commit()
    return redirect(url_for('portal_encuestador_participantes'))




# ------------------ ENCUESTAS ------------------ #

@app.route('/encuestas/<int:id_encuesta>')
def responder_encuestas_aviso(id_encuesta):
    cur = mysql.connection.cursor()
    cur.execute('SELECT nombre, descripcion FROM Encuestas WHERE id_encuesta = %s', [id_encuesta])
    data = cur.fetchone()
    cur.close()

    informacion = {
        'titulo_favicon': 'Encuesta de ' + data[0],
        'titulo' : data[0],
        'descripcion' : ' Para contestar esta encuesta, debes acceder como participante.',
        'texto_boton_izq' : 'Iniciar Sesión como Participante',
        'enlace_boton_izq' : '/iniciar-sesion',
        'texto_boton_der' : 'Regístrate como Participante',
        'enlace_boton_der' : '/registrarse'
    }
    return render_template("aviso-botones.html", informacion=informacion)

# NUEVO FORMULARIO DE ENCUESTAS
@app.route('/encuestas/<int:id_encuesta>/<correo>')
def responder_encuestas(id_encuesta, correo):
    cur = mysql.connection.cursor()
    cur.execute('SELECT nombre, descripcion, preguntas FROM Encuestas WHERE id_encuesta = %s', [id_encuesta])
    data = cur.fetchone()

    #Deberia ir al momento que Participante envìa la Encuesta con sus respuestas
    #cur.execute('INSERT INTO Responde(correo,id_encuesta) VALUES (%s,%s)',[correo,id_encuesta])
    
    cur.execute("SELECT P.id_pregunta, P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
    questions=cur.fetchall()
    
    cur.execute("SELECT A.id_alternativa,A.descripcion  FROM Alternativas as A,Preguntas as P,Encuestas as E  WHERE E.id_encuesta=%s AND P.id_encuesta=E.id_encuesta AND P.id_pregunta=A.id_pregunta",[id_encuesta])
    options=cur.fetchall()    

    cur.close()
    mysql.connection.commit()
    informacion = {
        'nombre' : data[0],
        'descripcion' : data[1],
        'preguntas' : data[2]
    }
    datos = {
        'id_encuesta': id_encuesta,
        'correo': correo
    }
    return render_template("responde.html",
        informacion=informacion,
        datos=datos,
        correo=correo,
        questions=questions,
        options=options) 

# EL USUARIO HA FINALIZADO UNA ENCUESTA
@app.route('/encuestas-finalizar/<int:id_encuesta>/<correo>')
def encuestas_finalizar(id_encuesta, correo):
    cur = mysql.connection.cursor()
    #cur.execute('INSERT INTO Responde (correo, id_encuesta) VALUES (%s,%s)',[correo, id_encuesta])
    cur.execute('SELECT nombre FROM Encuestas WHERE id_encuesta = %s', [id_encuesta])
    data = cur.fetchone()
    mysql.connection.commit()

    informacion = {
        'titulo_favicon': "¡Encuesta finalizada!",
        'titulo': "¡Gracias por tu opinión!",
        'descripcion': "La encuesta ''" + data[0] + "'' fue respondida exitosamente."
    }
    return render_template("aviso.html", informacion=informacion)

#PODEMOS VER LAS ULTIMAS ENCUESTAS QUE ESTAN ABIERTAS
@app.route('/ultimas-encuestas')
def ultimas_encuestas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_encuesta, nombre, descripcion, fecha_inicio, fecha_fin, preguntas FROM Encuestas WHERE estado='Abierta'")
    data = cur.fetchall()
    return render_template("ultimas-encuestas.html", data=data)

# EL ENCUESTADOR EDITA LA ENCUESTA DE LA BASE DE DATOS
#@app.route('/editar-encuesta/<int:id_encuesta>')
#def editar_encuesta(id_encuesta):
    #data = id_encuesta
    #return render_template("portal-encuestador-encuestas-editar.html", data=data)

#ELIMINAR ALTERNATIVAS DE BASE DE DATOS
@app.route('/eliminar-alternativas/<int:id_pregunta>')
def elimina_alternativas(id_pregunta):

    cur = mysql.connection.cursor() 
    cur.execute('DELETE FROM Alternativas WHERE id_pregunta = %s',[id_pregunta])
    mysql.connection.commit()
    return 1

#ELIMINA DE LA TABLA 'RESPUESTAS'
@app.route('/eliminar-respuestas')
def elimina_respuestas(id_pregunta):
    cur = mysql.connection.cursor() 
    cur.execute('DELETE FROM Respuestas WHERE id_pregunta = %s',[id_pregunta])
    mysql.connection.commit()
    return 1

#ELIMINAR PREGUNTAS DE BASE DE DATOS
@app.route('/eliminar-preguntas/<int:id_encuesta>')
def elimina_preguntas(id_encuesta):

    cur = mysql.connection.cursor() 
    cur.execute('SELECT p.id_pregunta FROM Preguntas as p WHERE p.id_encuesta  = %s',[id_encuesta])
    row = cur.fetchall()

    for i in row:
        elimina_respuestas(i[0])
        elimina_alternativas(i[0])

    cur2 = mysql.connection.cursor() 
    cur2.execute('DELETE FROM Preguntas WHERE id_encuesta = %s', [id_encuesta])
    mysql.connection.commit()

    return 1

@app.route('/eliminar-de-tabla-responde/')
def eliminar_de_tabla_responde(id_encuesta):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Responde WHERE id_encuesta = %s', [id_encuesta])
    return 1

# EL ENCUESTADOR ELIMINA LA ENCUESTA DE LA BASE DE DATOS
# Tipo = abierta,cerrada, por_realizar
@app.route('/eliminar-encuesta/<tipo>/<int:id_encuesta>')
def eliminar_encuesta(tipo, id_encuesta):

    curr = mysql.connection.cursor()
    curr.execute('SELECT p.id_pregunta FROM Preguntas as p WHERE p.id_encuesta  = %s',[id_encuesta])
    eliminar_de_tabla_responde(id_encuesta)
    elimina_preguntas(id_encuesta)
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Encuestas WHERE id_encuesta = %s', [id_encuesta])
    mysql.connection.commit()

    if tipo == "abierta":      
        ret = redirect(url_for('portal_encuestador_encuestas_abiertas'))
    elif tipo == "cerrada":
        
        ret = redirect(url_for('portal_encuestador_encuestas_finalizadas'))
    elif tipo == "por_realizar": 
        ret = redirect(url_for('portal_encuestador_encuestas_realizar'))
    return ret

#El usuario guarda la encuesta creada en la base de datos
@app.route("/guardar_encuesta/<int:question_number>", methods=['POST'])
def guardar_encuesta(question_number):
    if request.method == 'POST':
        title=request.form['title']
        description=request.form['description']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Encuestas (nombre,descripcion,preguntas,estado) VALUES (%s,%s,%s,'Por realizar')",(title,description,question_number))
        cur.execute("SELECT LAST_INSERT_ID()")
        lastInsert = cur.fetchall()
        code=lastInsert[0][0]

        for i in range(0,question_number):
            question=request.form['Pregunta'+str(i)]
            item1=request.form['item1-'+str(i)]
            item2=request.form['item2-'+str(i)]
            query="INSERT INTO Preguntas (id_encuesta,enunciado) VALUES ("+str(code)+",'"+question+"')"
            cur.execute(query)
            cur.execute("SELECT LAST_INSERT_ID()")
            lastInsert = cur.fetchall()            
            query="INSERT INTO Alternativas (id_pregunta,descripcion) VALUES ("+str(lastInsert[0][0])+",'"+item1+"')"
            cur.execute(query)
            query="INSERT INTO Alternativas (id_pregunta,descripcion) VALUES ("+str(lastInsert[0][0])+",'"+item2+"')"
            cur.execute(query)
        mysql.connection.commit()
        return redirect(url_for('portal_encuestador_encuestas_realizar'))

#El usuario guarda los cambios hechos al editar una encuesta
@app.route("/guardar_cambios_encuesta/<int:id_encuesta>", methods=['POST'])
def guardar_cambios_encuesta(id_encuesta):
    if request.method == 'POST':
        title=request.form['title']
        description=request.form['description']
        cur = mysql.connection.cursor()
        query="UPDATE Encuestas SET nombre='"+title+"',descripcion='"+description+"' WHERE id_encuesta ="+str(id_encuesta)
        cur.execute(query)
        cur.execute("SELECT P.id_pregunta FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
        questions=cur.fetchall()
        c=0
        for question in questions:
            question1=request.form['Pregunta'+str(c)]
            item1=request.form['item1-'+str(c)]
            c=c+1
            item2=request.form['item2-'+str(c)]
            query="UPDATE Preguntas SET enunciado='"+question1+"' WHERE id_pregunta ="+str(question[0])
            cur.execute(query)
            cur.execute("SELECT A.id_alternativa,A.descripcion FROM Alternativas as A,Preguntas as P  WHERE A.id_pregunta= P.id_pregunta AND P.id_pregunta="+str(question[0]))
            options=cur.fetchall()
            query="UPDATE Alternativas SET descripcion='"+item1+"' WHERE id_alternativa ="+str(options[0][0])
            cur.execute(query)
            query="UPDATE Alternativas SET descripcion='"+item2+"' WHERE id_alternativa ="+str(options[1][0])
            cur.execute(query)
            c=c+1
        mysql.connection.commit()
        return redirect(url_for('portal_encuestador_encuestas_realizar'))

@app.route('/resultados-alternativa')
def resultados_alternativa(id_alternativa):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(id_alternativa) FROM Respuestas as r WHERE r.id_alternativa =%s",[id_alternativa])
    a = cur.fetchone()
    return a[0]


# ------------------ USO DE SESIONES ------------------ #

# VERIFICA EL INICIO DE SESION DEL ENCUESTADOR
@app.route("/logear-participante", methods = ['GET','POST'])
def logear_participante():
    if request.method =='POST':
        email = request.form['correo']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Encuestados WHERE correo = %s', [email])
        user = cur.fetchone()
        cur.close()

        if user is not None:
            if email == user[0]:
                session['nombre'] = user[1] #Se le pasa el nombre al HTML del portal
                session['primer-nombre'] = primera_palabra(user[1])
                session['correo'] = user[0] #Se le pasa el correo al HTML del portal
                session['participante'] = True
                return redirect(url_for('portal_participante'))
            else: 
                informacion = {
                    'titulo_favicon': 'Error',
                    'titulo' : '¡Algo está mal escrito!',
                    'descripcion' : 'Correo no es válido.',
                    'texto_boton' : 'Volver a Iniciar Sesión',
                    'enlace_boton' : '/iniciar-sesion'
                } 
                return render_template("aviso-boton.html", informacion=informacion)
                 #Error en correo escrito o contraseña
        else:
            informacion = {
                    'titulo_favicon': 'Error',
                    'titulo' : '¡No eres parte de nosotros... todavía!',
                    'descripcion' : 'Correo no registrado como participante.',
                    'texto_boton' : 'Regístrate como participante',
                    'enlace_boton' : '/registrarse'
            } 
            return render_template("aviso-boton.html", informacion=informacion)
    return redirect(url_for('iniciar_sesion'))  

# VERIFICA EL INICIO DE SESION DEL ENCUESTADOR
@app.route("/logear-encuestador", methods = ['GET','POST'])
def logear_encuestador():
    if request.method =='POST':
        email = request.form['usuario']
        password = request.form['contraseña']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Encuestadores WHERE correo = %s', [email])
        user = cur.fetchone()
        cur.close()
        #print(user[2])

        if user is not None:
            if password == user[2]:
                session['nombre'] = user[1] #Se le pasa el nombre al HTML del portal
                session['primer-nombre'] = primera_palabra(user[1])
                session['correo'] = user[3] #Se le pasa el correo al HTML del portal
                session['encuestador'] = True
                return redirect(url_for('portal_encuestador'))
            else:
                informacion = {
                    'titulo_favicon': 'Error',
                    'titulo' : '¡Algo está mal escrito!',
                    'descripcion' : 'Usuario y/o contraseña no validos.',
                    'texto_boton' : 'Volver a Iniciar Sesión',
                    'enlace_boton' : '/iniciar-sesion-encuestador'
                } 
                return render_template("aviso-boton.html", informacion=informacion)
                 #Error en correo escrito o contraseña
        else:
            informacion = {
                    'titulo_favicon': 'Error',
                    'titulo' : '¡No eres parte de nosotros... todavía!',
                    'descripcion' : 'Correo no registrado como encuestador.',
                    'texto_boton' : 'Regístrate como encuestador',
                    'enlace_boton' : '/registrarse-encuestador'
                } 
            return render_template("aviso-boton.html", informacion=informacion)
                        
    return redirect(url_for('iniciar_sesion_encuestador'))      

# AL CERRAR SESION LOS DATOS DE LA SESION DE USUARIO SE ELIMINAN DE CACHE
@app.route('/cerrar-sesion/')
def cerrar_sesion():
    session['participante'] = False
    session['encuestador'] = False
    session.clear()
    return redirect(url_for("index"))




# ------------------ FUNCIONES COMUNES ------------------ #

# PODEMOS VER LAS ULTIMAS ENCUESTAS QUE ESTAN ABIERTAS EN EL INDEX
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_encuesta, nombre, descripcion FROM Encuestas WHERE estado='Abierta' LIMIT 3")
    data = cur.fetchall()
    return render_template("index.html", data=data)

# SE ELIMINA DE LA BASE DE DATOS EL CORREO QUE PERTENECE A LA TABLA 'RESPONDE'
@app.route('/borrar-correo-tabla-responde/<correo>')
def borrar_correo_tabla_responde(correo):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Responde WHERE correo = %s', [correo])
    cur = mysql.connection.commit()
    return 1

# EL USUARIO SE DA DE BAJA Y SE CONFIRMA SU DESUSCRIPCION
@app.route('/desuscribir/<correo>')
def desuscribir(correo):
    informacion = {
        'titulo_favicon': "Darse de baja",
        'titulo': "¡Lamentamos que te vayas!",
        'descripcion': "El correo " + correo + " fue dado de baja exitosamente."
    }
    cur = mysql.connection.cursor()
    borrar_correo_tabla_responde(correo)
    cur.execute('DELETE FROM Encuestados WHERE correo = %s', [correo])
    mysql.connection.commit()
    return render_template("aviso.html", informacion=informacion)

# PAGINAS QUE SOLO RETORNAN UN ARCHIVO HTML
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

@app.route('/responde')
def responde():
    return render_template("responde.html")

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

@app.route('/portal-encuestador-participantes-agregar')
def portal_encuestador_participantes_agregar():
    return render_template("portal-encuestador-participantes-agregar.html")

@app.route('/portal-encuestador-encuestas-crear')
def portal_encuestador_encuestas_crear():
    return render_template("portal-encuestador-encuestas-crear.html")

@app.route('/portal-encuestador-encuestas-visualizar')
def portal_encuestador_encuestas_visualizar():
    return render_template("portal-encuestador-encuestas-visualizar.html")

@app.route('/portal-encuestador-resultados')
def portal_encuestador_resultados():
    cur3 = mysql.connection.cursor()
    cur3.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Cerrada'" )
    Closed = cur3.fetchall()
    return render_template("portal-encuestador-resultados.html", Closed=Closed)

@app.route('/portal-encuestador-estadisticas')
def portal_encuestador_estadisticas():
    return render_template("portal-encuestador-estadisticas.html")

@app.route('/portal-encuestador-perfil')
def portal_encuestador_perfil():
    return render_template("portal-encuestador-perfil.html")

@app.route('/portal-encuestador-ajustes')
def portal_encuestador_ajustes():
    return render_template("portal-encuestador-ajustes.html")




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
app.secret_key = "mysecretkey"




# ------------------ FUNCIONES DE PYTHON ------------------ #

# ELIMINA TODOS LOS CARACTERES QUE UNA PALABRA O STRING NO NECESITE TENER
def procesar_texto(palabra):
    caracteres_especiales = "!#$%^&*()|@¢∞¬÷≠¬´“”" 
    for caracter in caracteres_especiales:
        palabra_sin_caracteres_especiales = palabra.replace(caracter, '')
    palabra_con_espacios = palabra_sin_caracteres_especiales.replace('%20', ' ')
    #print(palabra_con_espacios)
    return palabra_con_espacios

# ELIMINA TODOS LOS CARACTERES QUE UNA PALABRA O STRING NO NECESITE TENER
def primera_palabra(palabra):
    return palabra.split()[0]

def diferenciaDias(fecha):
    fecha_actual = date.today()
    #fecha_termino = date.fecha
    #diferencia = fecha_termino - fecha_actual
    return 3

def diferenciaNegativaDias(fecha):
    fecha_actual = date.today()
    #fecha_termino = date.fecha
    #diferencia = fecha_actual - fecha_termino
    return 2
    



# ------------------ MANEJO DE ERRORES ------------------ #

# MUESTRA LOS ERRORES CORRECTAMENTE
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




# SIN ESTO NO VIVIMOS
if __name__ == '__main__':
    app.register_error_handler(400, error_400)
    app.register_error_handler(401, error_401)
    app.register_error_handler(403, error_403)
    app.register_error_handler(404, error_404)
    app.register_error_handler(408, error_408)
    app.register_error_handler(410, error_410)
    app.register_error_handler(500, error_500)
    app.run(debug=True)
