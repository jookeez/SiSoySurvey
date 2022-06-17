from flask import render_template
from __main__ import app
from src.bd import mysql

# PODEMOS VER LAS ULTIMAS ENCUESTAS QUE ESTAN ABIERTAS EN EL INDEX
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_encuesta, nombre, descripcion FROM Encuestas WHERE estado='Abierta' LIMIT 3")
    data = cur.fetchall()
    return render_template("index.html", data=data)

@app.route('/conocenos')
def conocenos():
    return render_template("conocenos.html")

@app.route('/terminos')
def terminos():
    return render_template("terminos.html")

@app.route('/sprint1')
def sprint1():
    return render_template("sprint1.html")

@app.route('/sprint2')
def sprint2():
    return render_template("sprint2.html")