from flask import render_template, redirect, url_for, request, session
from __main__ import app
from src.bd import mysql
from src.funciones import identificar_tipo_usuario
import src.poll

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
                session['portal'] = True
                session['nombre'] = user[1] #Se le pasa el nombre al HTML del portal
                session['correo'] = user[0] #Se le pasa el correo al HTML del portal
                return redirect(url_for('portal_participante'))
            else: 
                informacion = {
                    'titulo_favicon': 'Error',
                    'titulo' : '¡Algo está mal escrito!',
                    'descripcion' : 'Correo no es válido.',
                    'texto_boton' : 'Volver a Iniciar Sesión',
                    'enlace_boton' : '/iniciar-sesion'
                } 
                return render_template("aviso/boton.html", informacion=informacion)
                 #Error en correo escrito o contraseña
        else:
            informacion = {
                    'titulo_favicon': 'Error',
                    'titulo' : '¡No eres parte de nosotros... todavía!',
                    'descripcion' : 'Correo no registrado como participante.',
                    'texto_boton' : 'Regístrate como participante',
                    'enlace_boton' : '/registrarse'
            } 
            return render_template("aviso/boton.html", informacion=informacion)
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

        if user is not None:
            if password == user[2]:
                session['portal'] = True
                session['nombre'] = user[1] #Se le pasa el nombre al HTML del portal
                session['correo'] = user[3] #Se le pasa el correo al HTML del portal
                return redirect(url_for('portal_encuestador'))
            else:
                informacion = {
                    'titulo_favicon': 'Error',
                    'titulo' : '¡Algo está mal escrito!',
                    'descripcion' : 'Usuario y/o contraseña no validos.',
                    'texto_boton' : 'Volver a Iniciar Sesión',
                    'enlace_boton' : '/iniciar-sesion-encuestador'
                } 
                return render_template("aviso/boton.html", informacion=informacion)
                 #Error en correo escrito o contraseña
        else:
            informacion = {
                    'titulo_favicon': 'Error',
                    'titulo' : '¡No eres parte de nosotros... todavía!',
                    'descripcion' : 'Correo no registrado como encuestador.',
                    'texto_boton' : 'Regístrate como encuestador',
                    'enlace_boton' : '/registrarse-encuestador'
                } 
            return render_template("aviso/boton.html", informacion=informacion)
                        
    return redirect(url_for('iniciar_sesion_encuestador'))      

# AL CERRAR SESION LOS DATOS DE LA SESION DE USUARIO SE ELIMINAN DE CACHE
@app.route('/cerrar-sesion/')
def cerrar_sesion():
    session['portal'] = False
    session.clear()
    return redirect(url_for("index"))

@app.route('/iniciar-sesion')
def iniciar_sesion():
    if 'portal' in session:
        usuario = identificar_tipo_usuario(session['correo'])
        if usuario == "encuestador":
            return redirect(url_for('portal_encuestador'))
        else:
            return redirect(url_for('portal_participante'))
    else:
        return render_template("sesion/participante.html")

@app.route('/iniciar-sesion-encuestador')
def iniciar_sesion_encuestador():
    if 'portal' in session:
        usuario = identificar_tipo_usuario(session['correo'])
        if usuario == "encuestador":
            return redirect(url_for('portal_encuestador'))
        else:
            return redirect(url_for('portal_participante'))
    else:
        return render_template("sesion/encuestador.html")

