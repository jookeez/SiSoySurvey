from flask import render_template, redirect, url_for, session
from __main__ import app
from src.funciones import identificar_tipo_usuario

# ------------------ REGISTRARSE ------------------ #

@app.route('/registrarse')
def registrarse():
    if 'portal' in session:
        usuario = identificar_tipo_usuario(session['correo'])
        if usuario == "encuestador":
            return redirect(url_for('portal_encuestador'))
        else:
            return redirect(url_for('portal_participante'))
    return render_template("registrarse/participante.html")

@app.route('/registrarse-encuestador')
def registrarse_encuestador():
    if 'portal' in session:
        usuario = identificar_tipo_usuario(session['correo'])
        if usuario == "encuestador":
            return redirect(url_for('portal_encuestador'))
        else:
            return redirect(url_for('portal_participante'))
    return render_template("registrarse/encuestador.html")