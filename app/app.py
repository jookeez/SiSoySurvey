from flask import Flask, render_template
app = Flask(__name__)

import src.bd
import src.participante
import src.encuestador
import src.encuestas
import src.correo
import src.registrarse
import src.sesion
import src.funciones
import src.errores

from src.bd import mysql
from src.errores import error_400
from src.errores import error_401
from src.errores import error_403
from src.errores import error_404
from src.errores import error_408
from src.errores import error_410
from src.errores import error_500


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


if __name__ == '__main__':
    app.register_error_handler(400, error_400)
    app.register_error_handler(401, error_401)
    app.register_error_handler(403, error_403)
    app.register_error_handler(404, error_404)
    app.register_error_handler(408, error_408)
    app.register_error_handler(410, error_410)
    app.register_error_handler(500, error_500)
    app.run(port=5000, debug=True)
