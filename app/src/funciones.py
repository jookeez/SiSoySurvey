from flask import redirect, session, url_for
from __main__ import app
import re

# ------------------ FUNCIONES DE PYTHON ------------------ #

# ELIMINA TODOS LOS CARACTERES QUE UNA PALABRA O STRING NO NECESITE TENER
def procesar_texto(palabra):
    caracteres_especiales = "!#$%^&*()|@¢∞¬÷≠¬´“”" 
    for caracter in caracteres_especiales:
        palabra_sin_caracteres_especiales = palabra.replace(caracter, '')
    palabra_con_espacios = palabra_sin_caracteres_especiales.replace('%20', ' ')
    return palabra_con_espacios

# SI ENCUENTRA UN @ ES ENCUESTADOR, SINO ES PARTICIPANTE
# search("1", "2") BUSCA UN CARACTER [1] EN EL STRING [2]
def identificar_tipo_usuario(correo):
    usuario = ""
    if re.search("@", str(correo)): 
        usuario = "participante"
    else:
        usuario = "encuestador"
    return usuario
