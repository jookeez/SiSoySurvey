from flask import render_template
from __main__ import app

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
    return render_template("aviso/boton.html", informacion=informacion), 400

@app.errorhandler(401)
def error_401(error):
    informacion = {
        'titulo_favicon': "Error 401",
        'titulo': "¡Necesitas autenticarte!",
        'descripcion': "Estas tratando de entrar a una página sin credenciales.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso/boton.html", informacion=informacion), 401

@app.errorhandler(403)
def error_403(error):
    informacion = {
        'titulo_favicon': "Error 403",
        'titulo': "¡Alerta de intruso!",
        'descripcion': "Estas tratando de entrar a una página sin autorización.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso/boton.html", informacion=informacion), 403

@app.errorhandler(404)
def error_404(error):
    informacion = {
        'titulo_favicon': "Error 404",
        'titulo': "¡Houston, tenemos un problema!",
        'descripcion': "La página que estas buscando no existe o no está disponible por el momento.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso/boton.html", informacion=informacion), 404

@app.errorhandler(408)
def error_408(error):
    informacion = {
        'titulo_favicon': "Error 408",
        'titulo': "¡Se nos quedó una letra en el camino!",
        'descripcion': "No pudimos recibir toda la información por completo. Intenta actualizar la página.",
        'texto_boton': "Actualizar página",
        'enlace_boton': "javascript:location.reload()"
    }
    return render_template("aviso/boton.html", informacion=informacion), 408

@app.errorhandler(410)
def error_410(error):
    informacion = {
        'titulo_favicon': "Error 410",
        'titulo': "¡Botamos la basura!",
        'descripcion': "La página que estas buscando fue eliminada.",
        'texto_boton': "Ir al HOME",
        'enlace_boton': "https://encuestas.jookeez.com"
    }
    return render_template("aviso/boton.html", informacion=informacion), 410

@app.errorhandler(500)
def error_500(error):
    informacion = {
        'titulo_favicon': "Error 500",
        'titulo': "¡Se cayó el sistema!",
        'descripcion': "Estamos teniendo problemas internos. ¡Volveremos pronto!",
    }
    return render_template("aviso/simple.html", informacion=informacion), 500

@app.errorhandler(503)
def error_503(error):
    informacion = {
        'titulo_favicon': "Error 503",
        'titulo': "¡Se cayó el sistema!",
        'descripcion': "Nuestro servidor no esta disponible en este momento.",
    }
    return render_template("aviso/simple.html", informacion=informacion), 503