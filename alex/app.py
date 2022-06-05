from flask import Flask , render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime
from modules import Poll




app = Flask(__name__)#-------> Main de la aplicación

#mysql connection
app.config['MYSQL_HOST']='103.195.100.230'
app.config['MYSQL_USER']='jookeezc_alejandro'
app.config['MYSQL_PASSWORD']='is2_gonzal0'
app.config['MYSQL_DB']='jookeezc_encuesta'
mysql = MySQL(app)

#settings
app.secret_key = "mysecretkey"

# Se inicializa el almacen de encuestas
#polls=SystemPoll()

#Variables Globales
lastPoll=Poll()# hace referencia a la ultima encuesta creada






@app.route("/")
def home():#----> pagina home
    return render_template('index.html')

#-------------------------------
#-------------------------------

#Operaciones con preguntas

#-------------------------------
#-------------------------------
@app.route("/crear_pregunta", methods=['POST'])
def crear_pregunta():
    
    code=lastPoll.getCode()
    lastPoll.setQuestion(lastPoll.getQuestion()+1)
    enunciado=request.form['enunciado']
    
    #print(enunciado)
    
    #query="INSERT INTO Preguntas (id_encuesta,enunciado) VALUES ("+str(code)+","+enunciado+")"
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Preguntas (id_encuesta,enunciado) VALUES (%s,%s)",(code,enunciado))
    mysql.connection.commit()

    query="UPDATE Encuestas SET preguntas="+str(lastPoll.getQuestion())+" WHERE id_encuesta ="+str(code)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    
    return redirect(url_for('nueva_encuesta_code', code = lastPoll.getCode()))

#-------------------------------
@app.route("/enunciado_pregunta", methods=['POST'])
def enunciado_pregunta():
    
    code=lastPoll.getCode()
    lastPoll.setQuestion(lastPoll.getQuestion()+1)
    enunciado=request.form['enunciado']
     
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Preguntas (id_encuesta,enunciado) VALUES (%s,%s)",(code,enunciado))
    mysql.connection.commit()

    query="UPDATE Encuestas SET  preguntas="+str(lastPoll.getQuestion())+" WHERE id_encuesta ="+str(code)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
   
    
    
    return redirect(url_for('nueva_encuesta_code', code = code))

@app.route("/nueva_pregunta/<num>", methods=['POST'])
def nueva_pregunta(num):
    if request.method =='POST':
        
    
        title=request.form['title']
        des=request.form['description']
        
    
        
        for i in range(lastPoll.getQuestion()):
            question=request.form['question'+str(i)]

            cur = mysql.connection.cursor()
            query="UPDATE Preguntas SET enunciado='"+str(question)+"' WHERE id_encuesta ="+str(num)
            print(query)
            cur.execute(query)
            
            
        

        lastPoll.setQuestion(lastPoll.getQuestion()+1)

        query="UPDATE Encuestas SET nombre='"+str(title)+"',descripcion='"+str(des)+"',  preguntas="+str(lastPoll.getQuestion())+" WHERE id_encuesta ="+str(num)
        cur = mysql.connection.cursor()
        cur.execute(query)
        
        
        
        enunciado="''"
        query="INSERT INTO Preguntas (id_encuesta,enunciado) VALUES ("+str(num)+","+enunciado+")"
        print(query)
        cur.execute(query)
        cur.execute("SELECT LAST_INSERT_ID()")
        code = cur.fetchall()
        Lastquestion=0
        for row in code:
            Lastquestion=row[0]

        query="INSERT INTO Alternativas (id_pregunta,descripcion) VALUES ("+str(Lastquestion)+","+enunciado+")"
        print(query)
        cur.execute(query)

        query="INSERT INTO Alternativas (id_pregunta,descripcion) VALUES ("+str(Lastquestion)+","+enunciado+")"
        print(query)
        cur.execute(query)


        mysql.connection.commit()
        return redirect(url_for('nueva_encuesta_code', code=num))

    



#-------------------------------

#-------------------------------
#-------------------------------

#Operaciones con Encuestas

#-------------------------------
#-------------------------------

@app.route("/encuestas")
def encuestas():#----> pagina

    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Por realizar'")
    
    Ready = cur1.fetchall()

    
    
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Abierta'")
    Open = cur2.fetchall()

    cur3 = mysql.connection.cursor()
    cur3.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Cerrada'" )
    Closed = cur3.fetchall()
    
    
    
    
    return render_template("encuestas.html",
        pollsReady=Ready,
        pollsOpen=Open,
        pollsClosed=Closed)

#-------------------------------

@app.route("/responder_encuesta/<id_encuesta>") #, methods=['POST']
def responder_encuesta(id_encuesta):
    cur = mysql.connection.cursor()
    cur.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.id_encuesta=%s",[id_encuesta])
    polls = cur.fetchall()

    cur.execute("SELECT P.id_pregunta, P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
    questions=cur.fetchall()
    
    cur.execute("SELECT A.id_alternativa,A.descripcion  FROM Alternativas as A,Preguntas as P,Encuestas as E  WHERE E.id_encuesta=%s AND P.id_encuesta=E.id_encuesta AND P.id_pregunta=A.id_pregunta",[id_encuesta])
    options=cur.fetchall()

    return render_template("responder_encuesta.html"
    ,polls=polls
    ,questions=questions
    ,options=options
    ,id_encuesta=id_encuesta)

#-------------------------------




#-------------------------------
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
            print(query)
            cur.execute(query)

        mysql.connection.commit()
        return redirect(url_for('encuestas'))
#-------------------------------
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
            print('Pregunta'+str(c))
            
            question1=request.form['Pregunta'+str(c)]
            print('item1-'+str(c))
            
            item1=request.form['item1-'+str(c)]
            c=c+1
            print('item2-'+str(c))
            item2=request.form['item2-'+str(c)]
            
            query="UPDATE Preguntas SET enunciado='"+question1+"' WHERE id_pregunta ="+str(question[0])
            print(query)
            cur.execute(query)

            cur.execute("SELECT A.id_alternativa,A.descripcion FROM Alternativas as A,Preguntas as P  WHERE A.id_pregunta= P.id_pregunta AND P.id_pregunta="+str(question[0]))
            options=cur.fetchall()
            
            query="UPDATE Alternativas SET descripcion='"+item1+"' WHERE id_alternativa ="+str(options[0][0])
            cur.execute(query)
            query="UPDATE Alternativas SET descripcion='"+item2+"' WHERE id_alternativa ="+str(options[1][0])
            cur.execute(query)
            c=c+1
        mysql.connection.commit()
        return redirect(url_for('visualizar_encuesta',id_encuesta))
#-------------------------------



#-------------------------------
@app.route("/nueva_encuesta/<int:question_number>")
def nueva_encuesta(question_number):
    return render_template("nueva_encuesta.html",question_number=question_number)
    

#-------------------------------

@app.route("/editar_encuesta/<id_encuesta>") #, methods=['POST']
def editar_encuesta(id_encuesta):
    cur = mysql.connection.cursor()
    cur.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.id_encuesta=%s",[id_encuesta])
    polls = cur.fetchall()

    cur.execute("SELECT P.id_pregunta, P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
    questions=cur.fetchall()

    cur.execute("SELECT A.id_alternativa,A.descripcion  FROM Alternativas as A,Preguntas as P,Encuestas as E  WHERE E.id_encuesta=%s AND P.id_encuesta=E.id_encuesta AND P.id_pregunta=A.id_pregunta",[id_encuesta])
    options=cur.fetchall()

    return render_template("editar_encuesta.html"
    ,polls=polls
    ,questions=questions
    ,options=options
    ,id_encuesta=id_encuesta)



#-------------------------------
#-------------------------------

@app.route("/visualizar_encuesta/<id_encuesta>") #, methods=['POST']
def visualizar_encuesta(id_encuesta):
    cur = mysql.connection.cursor()
    cur.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.id_encuesta=%s",[id_encuesta])
    polls = cur.fetchall()

    cur.execute("SELECT P.id_pregunta, P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[id_encuesta])
    questions=cur.fetchall()

    cur.execute("SELECT A.id_alternativa,A.descripcion  FROM Alternativas as A,Preguntas as P,Encuestas as E  WHERE E.id_encuesta=%s AND P.id_encuesta=E.id_encuesta AND P.id_pregunta=A.id_pregunta",[id_encuesta])
    options=cur.fetchall()

    return render_template("visualizar_encuesta.html"
    ,polls=polls
    ,questions=questions
    ,options=options
    ,id_encuesta=id_encuesta)

#-------------------------------

@app.route('/eliminar_encuesta/<num>')
def eliminar_encuesta(num):
    
    query='DELETE FROM Preguntas WHERE id_encuesta ='+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)

    query='DELETE FROM Encuestas WHERE id_encuesta ='+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()

    return redirect(url_for('encuestas'))

#-------------------------------

@app.route('/enviar_encuesta/<num>')
def enviar_encuesta(num):
   
    query="UPDATE Encuestas SET estado='Abierta' WHERE id_encuesta ="+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    
    return redirect(url_for('encuestas'))

#-------------------------------

@app.route('/cerrar_encuesta/<num>')
def cerrar_encuesta(num):
   
    query="UPDATE Encuestas SET estado='Cerrada' WHERE id_encuesta ="+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    
    return redirect(url_for('encuestas'))

#-------------------------------
#-------------------------------

# Operaciones con Encuestados

#-------------------------------
#-------------------------------

@app.route('/encuestados')
def encuestados():
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados')
    data = cur.fetchall()
    
    return render_template("encuestados.html", encuestados = data)#'encuestados'

#-------------------------------

@app.route('/encuestados/<name>')
def estadoEncuestados(name):
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados')
    data = cur.fetchall()
    return render_template("encuestados.html", encuestados = data)#'encuestados'

#-------------------------------

@app.route('/nuevo_enc', methods=['POST'])
def nuevo_enc():
    
    if request.method == 'POST':

        correo = request.form['correo']
        nombre = request.form['nombre']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO Encuestados (correo,nombre) VALUES (%s,%s)',(correo,nombre))
        mysql.connection.commit()

    return redirect(url_for('encuestados'))

#-------------------------------
    
@app.route('/editar_encuestado/<email>')
def get_encuestado(email):

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados WHERE correo = %s', [email])
    data = cur.fetchall()
    return render_template('e-encuestado.html', encuestado = data[0])

#-------------------------------

@app.route('/eliminar_encuestado/<email>')
def elim_encuestado(email):

    cur = mysql.connection.cursor()
    
    cur.execute('DELETE FROM Encuestados WHERE correo = %s',[email])
    mysql.connection.commit()
    
    return redirect(url_for('encuestados'))

#-------------------------------
#-------------------------------
#Login

#-------------------------------
#-------------------------------

@app.route("/login")
def login():
    return render_template("login.html")

#-------------------------------

@app.route("/sigin")
def sigin():
    return render_template("sigin.html")

#-------------------------------
#-------------------------------


#Operaciónes con encuestas


#-------------------------------
'''

@app.route("/nueva_encuesta/<code>")
def nueva_encuesta_code(code):
   
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.id_encuesta=%s",[code])

    polln = cur1.fetchall()
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[code])
    questionn=cur2.fetchall()
    

    return render_template("nueva_encuesta.html"
    ,polln=polln
    ,questionn=questionn)

#-------------------------------
@app.route("/cancelar_nueva_encuesta")
def cancelar_nueva_encuesta():


    query='DELETE FROM Preguntas WHERE id_encuesta ='+str(lastPoll.getCode())
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    query='DELETE FROM Encuestas WHERE id_encuesta ='+str(lastPoll.getCode())
    cur.execute(query)
    mysql.connection.commit()
    

    return redirect(url_for('encuestas'))

@app.route("/crear_encuesta/<num>", methods=['POST'])
def crear_encuesta(num):
    
    if request.method =='POST':
        print(".")
        print(".")
        print(".")
        print(".")
        print("Recogi lo siguiente:")
        print(num)
        title=request.form['title']
        des=request.form['description']
        
            
        print(title)
        print(des)
        
        for i in range(lastPoll.getQuestion()):
            print('question'+str(i))
            #questions.append(request.form['question'+str(i)])
            #print(request.form['question'+str(i)])
            cur = mysql.connection.cursor()
            query="UPDATE Preguntas SET enunciado='"+str(request.form['question'+str(i)])+"' WHERE id_encuesta ="+str(num)
            print(query)
            cur.execute(query)
            mysql.connection.commit()
            
        

        

        query="UPDATE Encuestas SET nombre='"+str(title)+"',descripcion='"+str(des)+"' WHERE id_encuesta ="+str(num)
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        

    return redirect(url_for('encuestas'))


'''


