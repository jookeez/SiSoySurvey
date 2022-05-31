from flask import Flask , render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)#-------> Main de la aplicación

app.config['MYSQL_HOST']='103.195.100.230'
app.config['MYSQL_USER']='jookeezc_patricio'
app.config['MYSQL_PASSWORD']='is2_gonzal0'
app.config['MYSQL_DB']='jookeezc_encuesta'

mysql = MySQL(app)
#Ingreso mail, del mail que me de el id_encuesta
@app.route("/encuestas_encuestado/<mail>")
def encuestas_encuestado(mail):

    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT Enc.id_encuesta,Enc.nombre,Enc.descripcion, Enc.estado,Enc.preguntas  FROM(   SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Por realizar') as Enc ,(SELECT r.id_encuesta FROM Responde as r WHERE r.correo = %s ) as Res WHERE Res.id_encuesta=Enc.id_encuesta ",[mail])
    data = cur1.fetchall()
    for row in data:
        print(row[0])
        text = ""
    
    p = data
    
    return render_template("encuestas.html",data=p)

       
if __name__ == '__main__':
    app.run(port = 3000, debug = True)
