from flask import render_template, redirect, url_for, request, session
from flask_mail import Message
from __main__ import app
from src.bd import mysql
from src.correo import mail

# ------------------ ENCUESTADOR ------------------ #

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
            return render_template("aviso/boton.html", informacion=informacion)

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
        mensaje.html = render_template("mail/verificar.html", data=data)
        mail.send(mensaje)
        return redirect(url_for('portal_encuestador_participantes_agregar'))

# MUESTRA EL LISTADO DE PARTICIPANTES EN EL PORTAL DEL ENCUESTADOR
@app.route('/portal-encuestador-participantes-listado')
def portal_encuestador_participantes_listado():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados')
    data = cur.fetchall()
    return render_template("portal/encuestador/participantes-listado.html", encuestados=data)

# MUESTRA EL LISTADO DE ENCUESTAS POR REALIZAR
@app.route('/portal-encuestador-encuestas-realizar')
def portal_encuestador_encuestas_realizar():
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Por realizar'")
    Ready = cur1.fetchall()
    return render_template("portal/encuestador/encuestas-realizar.html", Ready=Ready)

# MUESTRA EL LISTADO DE ENCUESTAS ABIERTAS
@app.route('/portal-encuestador-encuestas-abiertas')
def portal_encuestador_encuestas_abiertas():
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Abierta'")
    Open = cur2.fetchall()
    return render_template("portal/encuestador/encuestas-abiertas.html", Open=Open)

# MUESTRA EL LISTADO DE ENCUESTAS FINALIZADAS
@app.route('/portal-encuestador-encuestas-finalizadas')
def portal_encuestador_encuestas_finalizadas():
    cur3 = mysql.connection.cursor()
    cur3.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Cerrada'" )
    Closed = cur3.fetchall()
    return render_template("portal/encuestador/encuestas-finalizadas.html", Closed=Closed)

# EL ENCUESTADOR CAMBIA SU NOMBRE EN EL PORTAL
@app.route("/cambiar-nombre-encuestador/<correo>", methods=['POST'])
def cambiar_nombre_encuestador(correo):
    if request.method =='POST':
        nuevo_nombre = request.form['nuevo_nombre']
        if len(nuevo_nombre) > 1:
            cur = mysql.connection.cursor()
            cur.execute('UPDATE Encuestadores SET nombre = %s WHERE correo = %s',[nuevo_nombre, correo])
            mysql.connection.commit()
            session['nombre'] = nuevo_nombre
            return redirect(url_for('portal_encuestador_perfil'))
        else:
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
            return render_template("aviso/simple.html", informacion=informacion)
        else:
            # ENVIAR MENSAJE AL USUARIO
            return redirect(url_for('portal_encuestador_perfil'))
    else:
        return redirect(url_for('portal_encuestador_perfil'))


#El usuario accede al portal de creacion de encuestas
@app.route("/portal-encuestador-encuestas-crear/<int:question_number>")
def nueva_encuesta(question_number):
    return render_template("portal/encuestador/encuestas-crear.html",question_number=question_number)


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

    return render_template("portal/encuestador/encuestas-editar.html"
    ,polls=polls
    ,questions=questions
    ,options=options
    ,id_encuesta=id_encuesta)


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

    return render_template("portal/encuestador/encuestas-visualizar.html"
    ,polls=polls
    ,questions=questions
    ,options=options
    ,id_encuesta=id_encuesta)


@app.route('/portal-encuestador')
def portal_encuestador():
    return render_template("portal/encuestador/index.html")

@app.route('/portal-encuestador-participantes-agregar')
def portal_encuestador_participantes_agregar():
    return render_template("portal/encuestador/participantes-agregar.html")

@app.route('/portal-encuestador-encuestas-crear')
def portal_encuestador_encuestas_crear():
    return render_template("portal/encuestador/encuestas-crear.html")

@app.route('/portal-encuestador-encuestas-visualizar')
def portal_encuestador_encuestas_visualizar():
    return render_template("portal/encuestador/encuestas-visualizar.html")

#@app.route('/portal-encuestador-encuestas-editar')
#def portal_encuestador_encuestas_editar():
#    return render_template("portal/encuestador/encuestas-editar.html")

@app.route('/portal-encuestador-resultados')
def portal_encuestador_resultados():
    return render_template("portal/encuestador/resultados.html")

@app.route('/portal-encuestador-estadisticas')
def portal_encuestador_estadisticas():
    return render_template("portal/encuestador/estadisticas.html")

@app.route('/portal-encuestador-perfil')
def portal_encuestador_perfil():
    return render_template("portal/encuestador/perfil.html")

@app.route('/portal-encuestador-ajustes')
def portal_encuestador_ajustes():
    return render_template("portal/encuestador/ajustes.html")