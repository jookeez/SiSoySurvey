from flask import Blueprint, render_template
basico = Blueprint('basico', __name__)

#PAGINAS QUE SOLO RETORNAN UN ARCHIVO HTML
@basico.route('/')
def index():
    return render_template("index.html")

@basico.route('/iniciar-sesion')
def iniciar_sesion():
    return render_template("iniciar-sesion.html")

@basico.route('/iniciar-sesion-encuestador')
def iniciar_sesion_encuestador():
    return render_template("iniciar-sesion-encuestador.html")

@basico.route('/registrarse')
def registrarse():
    return render_template("registrarse.html")

@basico.route('/registrarse-encuestador')
def registrarse_encuestador():
    return render_template("registrarse-encuestador.html")

@basico.route('/conocenos')
def conocenos():
    return render_template("conocenos.html")

@basico.route('/ultimas-encuestas')
def ultimas_encuestas():
    return render_template("ultimas-encuestas.html")

@basico.route('/terminos')
def terminos():
    return render_template("terminos.html")

@basico.route('/portal-participante')
def portal_participante():
    return render_template("portal-participante.html")

@basico.route('/portal-participante-encuestas')
def portal_participante_encuestas():
    return render_template("portal-participante-encuestas.html")

@basico.route('/portal-participante-respondidas')
def portal_participante_respondidas():
    return render_template("portal-participante-respondidas.html")

@basico.route('/portal-participante-perfil')
def portal_participante_perfil():
    return render_template("portal-participante-perfil.html")

@basico.route('/portal-participante-ajustes')
def portal_participante_ajustes():
    return render_template("portal-participante-ajustes.html")

@basico.route('/portal-encuestador')
def portal_encuestador():
    return render_template("portal-encuestador.html")

@basico.route('/portal-encuestador-resultados')
def portal_encuestador_resultados():
    return render_template("portal-encuestador-resultados.html")

@basico.route('/portal-encuestador-estadisticas')
def portal_encuestador_estadisticas():
    return render_template("portal-encuestador-estadisticas.html")

@basico.route('/portal-encuestador-perfil')
def portal_encuestador_perfil():
    return render_template("portal-encuestador-perfil.html")

@basico.route('/portal-encuestador-ajustes')
def portal_encuestador_ajustes():
    return render_template("portal-encuestador-ajustes.html")