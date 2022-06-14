from flask import render_template, redirect, url_for, request, session
from __main__ import app
from src.bd import mysql

# ------------------ PARTICIPANTE ------------------ #

# VEMOS EN EL PORTAL PRIVADO DEL PARTICIPANTE EL LISTADO DE ENCUESTAS QUE PUEDE RESPONDER
@app.route("/portal-participante-encuestas-responder/<mail>")
def encuestas_encuestado(mail):
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT Enc.id_encuesta,Enc.nombre,Enc.descripcion, Enc.estado,Enc.preguntas  FROM(   SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Abierta') as Enc ,(SELECT r.id_encuesta FROM Responde as r WHERE r.correo = %s ) as Res WHERE Res.id_encuesta=Enc.id_encuesta ",[mail])
    data = cur1.fetchall()
    return render_template("portal/participante/encuestas-responder.html", data=data,mail=mail)

# VEMOS EN EL PORTAL PRIVADO DEL PARTICIPANTE EL LISTADO DE ENCUESTAS QUE YA RESPONDIÓ
@app.route('/portal-participante-encuestas-respondidas/<mail>')
def encuestas_respondidas_participante(mail):
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT Enc.id_encuesta,Enc.nombre,Enc.descripcion, Enc.estado,Enc.preguntas  FROM(   SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Cerrada') as Enc ,(SELECT r.id_encuesta FROM Responde as r WHERE r.correo = %s ) as Res WHERE Res.id_encuesta=Enc.id_encuesta ",[mail])
    data = cur1.fetchall()
    return render_template("portal/participante/encuestas-respondidas.html", data=data)

# EL PARTICIPANTE CAMBIA SU NOMBRE EN EL PORTAL
@app.route("/cambiar-nombre-participante/<correo>", methods=['POST'])
def cambiar_nombre_participante(correo):
    if request.method =='POST':
        nuevo_nombre = request.form['nuevo_nombre']
        if len(nuevo_nombre) > 1:
            cur = mysql.connection.cursor()
            cur.execute('UPDATE Encuestados SET nombre = %s WHERE correo = %s',[nuevo_nombre, correo])
            mysql.connection.commit()
            session['nombre'] = nuevo_nombre
            return redirect(url_for('portal_participante_perfil'))
        else:
            return redirect(url_for('portal_participante_perfil'))

# EL ENCUESTADOR ELIMINA AL PARTICIPANTE DE LA BASE DE DATOS
@app.route('/eliminar-participante/<correo>')
def eliminar_participante(correo):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Encuestados WHERE correo = %s', [correo])
    mysql.connection.commit()
    return redirect(url_for('portal_encuestador_participantes'))

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
    return render_template("aviso/simple.html", informacion=informacion)


@app.route('/portal-participante')
def portal_participante():
    return render_template("portal/participante/index.html")

@app.route('/portal-participante-encuestas-responder')
def portal_participante_encuestas_responder():
    return render_template("portal/participante/encuestas-responder.html")

@app.route('/portal-participante-encuestas-respondidas')
def portal_participante_encuestas_respondidas():
    return render_template("portal/participante/encuestas-respondidas.html")

@app.route('/portal-participante-perfil')
def portal_participante_perfil():
    return render_template("portal/participante/perfil.html")

@app.route('/portal-participante-ajustes')
def portal_participante_ajustes():
    return render_template("portal/participante/ajustes.html")