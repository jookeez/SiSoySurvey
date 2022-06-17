from flask import Flask, render_template
from gevent.pywsgi import WSGIServer
app = Flask(__name__)

import src.bd
import src.participante
import src.encuestador
import src.encuestas
import src.correo
import src.registrarse
import src.sesion
import src.otros
import src.funciones
import src.errores

from src.errores import error_400
from src.errores import error_401
from src.errores import error_403
from src.errores import error_404
from src.errores import error_408
from src.errores import error_410
from src.errores import error_500

if __name__ == '__main__':
    app.register_error_handler(400, error_400)
    app.register_error_handler(401, error_401)
    app.register_error_handler(403, error_403)
    app.register_error_handler(404, error_404)
    app.register_error_handler(408, error_408)
    app.register_error_handler(410, error_410)
    app.register_error_handler(500, error_500)

    # Debug/Development
    app.run(debug=True)

    # Production
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()
