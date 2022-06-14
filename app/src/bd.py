from calendar import c
from flask_mysqldb import MySQL
from __main__ import app
import config

# CONEXION SQL
app.config['MYSQL_HOST'] = config.BD_HOST
app.config['MYSQL_USER'] = config.BD_USER
app.config['MYSQL_PASSWORD'] = config.BD_PASSWD
app.config['MYSQL_DB'] = config.BD_NAME
mysql = MySQL(app)