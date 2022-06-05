CREATE TABLE Respuestas(
    id_pregunta int,
    id_alternativa int,
    FOREIGN KEY (id_pregunta) REFERENCES Preguntas(id_pregunta),
    FOREIGN KEY (id_alternativa) REFERENCES Alternativas(id_alternativa)
);


SELECT A.descripcion FROM Alternativas as A,Preguntas as P,Encuestas as E  WHERE E.id_encuesta=3 AND P.id_encuesta=E.id_encuesta AND P.id_pregunta=A.id_pregunta;

SELECT A.id_alternativa,A.descripcion FROM Alternativas as A,Preguntas as P  WHERE A.id_pregunta= P.id_pregunta AND P.id_pregunta=88;





INSERT INTO Alternativas(id_alternativa,descripcion,id_pregunta) 
VALUES (5,'Un manjar',4);
INSERT INTO Alternativas(id_alternativa,descripcion,id_pregunta) 
VALUES (6,'No y tu mama?',4);

INSERT INTO Alternativas(id_alternativa,descripcion,id_pregunta) 
VALUES (7,'si',8);
INSERT INTO Alternativas(id_alternativa,descripcion,id_pregunta) 
VALUES (8,'No',8);



