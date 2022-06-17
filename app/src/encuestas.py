from flask import render_template, redirect, url_for, request
from __main__ import app
from src.bd import mysql

# ------------------ ENCUESTAS ------------------ #

@app.route('/encuestas/<int:id_encuesta>')
def responder_encuestas_aviso(id_encuesta):
    cur = mysql.connection.cursor()
    cur.execute('SELECT nombre, descripcion FROM Encuestas WHERE id_encuesta = %s', [id_encuesta])
    data = cur.fetchone()
    cur.close()

    informacion = {
        'titulo_favicon': 'Encuesta de ' + data[0],
        'titulo' : data[0],
        'descripcion' : data[1] + ' Para contestar esta encuesta, debes acceder como participante.',
        'texto_boton_izq' : 'Iniciar Sesión como Participante',
        'enlace_boton_izq' : '/iniciar-sesion',
        'texto_boton_der' : 'Regístrate como Participante',
        'enlace_boton_der' : '/registrarse'
    }
    return render_template("aviso/botones.html", informacion=informacion)

# NUEVO FORMULARIO DE ENCUESTAS
@app.route('/encuestas/<int:id_encuesta>/<correo>')
def responder_encuestas(id_encuesta, correo):
    cur = mysql.connection.cursor()
    cur.execute('SELECT nombre, descripcion, preguntas FROM Encuestas WHERE id_encuesta = %s', [id_encuesta])
    data = cur.fetchone()

    cur.execute('INSERT INTO Responde(correo,id_encuesta) VALUES (%s,%s)',[correo, id_encuesta])
    
    cur.execute("SELECT P.id_pregunta, P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
    questions=cur.fetchall()
    
    cur.execute("SELECT A.id_alternativa,A.descripcion  FROM Alternativas as A,Preguntas as P,Encuestas as E  WHERE E.id_encuesta=%s AND P.id_encuesta=E.id_encuesta AND P.id_pregunta=A.id_pregunta",[id_encuesta])
    options=cur.fetchall()    
    

    cur.close()
    mysql.connection.commit()
    informacion = {
        'nombre' : data[0],
        'descripcion' : data[1],
        'preguntas' : data[2]
    }
    return render_template("encuestas/responde.html"
    ,informacion=informacion
    ,questions=questions
    ,options=options) 

# EL ENCUESTADOR EDITA LA ENCUESTA DE LA BASE DE DATOS
#@app.route('/editar-encuesta/<int:id_encuesta>')
#def editar_encuesta(id_encuesta):
    #data = id_encuesta
    #return render_template("portal/encuestador/encuestas-editar.html", data=data)

#ELIMINAR ALTERNATIVAS DE BASE DE DATOS
@app.route('/eliminar-alternativas/<int:id_pregunta>')
def elimina_alternativas(id_pregunta):

    cur = mysql.connection.cursor() 
    cur.execute('DELETE FROM Alternativas WHERE id_pregunta = %s',[id_pregunta])
    mysql.connection.commit()
    return 1

#ELIMINAR PREGUNTAS DE BASE DE DATOS
@app.route('/eliminar-preguntas/<int:id_encuesta>')
def elimina_preguntas(id_encuesta):

    cur = mysql.connection.cursor() 
    cur.execute('SELECT p.id_pregunta FROM Preguntas as p WHERE p.id_encuesta  = %s',[id_encuesta])
    row = cur.fetchall()

    for i in row:
        elimina_alternativas(i[0])

    cur2 = mysql.connection.cursor() 
    cur2.execute('DELETE FROM Preguntas WHERE id_encuesta = %s', [id_encuesta])
    mysql.connection.commit()

    return 1

# EL ENCUESTADOR ELIMINA LA ENCUESTA DE LA BASE DE DATOS
# Tipo = abierta, cerrada, por_realizar
@app.route('/eliminar-encuesta/<tipo>/<int:id_encuesta>')
def eliminar_encuesta(tipo, id_encuesta):

    curr = mysql.connection.cursor()
    curr.execute('SELECT p.id_pregunta FROM Preguntas as p WHERE p.id_encuesta  = %s',[id_encuesta])
    elimina_preguntas(id_encuesta)
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Encuestas WHERE id_encuesta = %s', [id_encuesta])
    mysql.connection.commit()

    if tipo == "abierta":      
        ret = redirect(url_for('portal_encuestador_encuestas_abiertas'))
    elif tipo == "cerrada":      
        ret = redirect(url_for('portal_encuestador_encuestas_finalizadas'))
    elif tipo == "por_realizar": 
        ret = redirect(url_for('portal_encuestador_encuestas_realizar'))
    return ret

#El usuario guarda la encuesta creada en la base de datos
@app.route("/guardar_encuesta/<int:question_number>", methods=['POST'])
def guardar_encuesta(question_number):
    if request.method == 'POST':
        title=request.form['title']
        description=request.form['description']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Encuestas (nombre,descripcion,preguntas,estado) VALUES (%s,%s,%s,'Por realizar')",(title,description,question_number))
        cur.execute("SELECT LAST_INSERT_ID()")
        lastInsert = cur.fetchall()
        code=lastInsert[0][0]

        for i in range(0,question_number):
            question=request.form['Pregunta'+str(i)]
            item1=request.form['item1-'+str(i)]
            item2=request.form['item2-'+str(i)]
            query="INSERT INTO Preguntas (id_encuesta,enunciado) VALUES ("+str(code)+",'"+question+"')"
            cur.execute(query)
            cur.execute("SELECT LAST_INSERT_ID()")
            lastInsert = cur.fetchall()            
            query="INSERT INTO Alternativas (id_pregunta,descripcion) VALUES ("+str(lastInsert[0][0])+",'"+item1+"')"
            cur.execute(query)
            query="INSERT INTO Alternativas (id_pregunta,descripcion) VALUES ("+str(lastInsert[0][0])+",'"+item2+"')"
            cur.execute(query)
        mysql.connection.commit()
        return redirect(url_for('portal_encuestador_encuestas_realizar'))

#El usuario guarda los cambios hechos al editar una encuesta
@app.route("/guardar_cambios_encuesta/<int:id_encuesta>", methods=['POST'])
def guardar_cambios_encuesta(id_encuesta):
    if request.method == 'POST':
        title=request.form['title']
        description=request.form['description']
        cur = mysql.connection.cursor()
        query="UPDATE Encuestas SET nombre='"+title+"',descripcion='"+description+"' WHERE id_encuesta ="+str(id_encuesta)
        cur.execute(query)
        cur.execute("SELECT P.id_pregunta FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
        questions=cur.fetchall()
        c=0
        for question in questions:
            question1=request.form['Pregunta'+str(c)]
            item1=request.form['item1-'+str(c)]
            c=c+1
            item2=request.form['item2-'+str(c)]
            query="UPDATE Preguntas SET enunciado='"+question1+"' WHERE id_pregunta ="+str(question[0])
            cur.execute(query)
            cur.execute("SELECT A.id_alternativa,A.descripcion FROM Alternativas as A,Preguntas as P  WHERE A.id_pregunta= P.id_pregunta AND P.id_pregunta="+str(question[0]))
            options=cur.fetchall()
            query="UPDATE Alternativas SET descripcion='"+item1+"' WHERE id_alternativa ="+str(options[0][0])
            cur.execute(query)
            query="UPDATE Alternativas SET descripcion='"+item2+"' WHERE id_alternativa ="+str(options[1][0])
            cur.execute(query)
            c=c+1
        mysql.connection.commit()
        return redirect(url_for('portal_encuestador_encuestas_realizar'))


@app.route('/responde')
def responde():
    return render_template("encuestas/responde.html")


#PODEMOS VER LAS ULTIMAS ENCUESTAS QUE ESTAN ABIERTAS
@app.route('/ultimas-encuestas')
def ultimas_encuestas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_encuesta, nombre, descripcion, fecha_inicio, fecha_fin, preguntas FROM Encuestas WHERE estado='Abierta'")
    data = cur.fetchall()
    return render_template("encuestas/ultimas-encuestas.html", data=data)