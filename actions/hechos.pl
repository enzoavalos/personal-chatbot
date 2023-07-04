ocupado('lunes',9,12,'cursando').
ocupado('martes',10,18,'cursando').
ocupado('miercoles',9,16,'cursando').
ocupado('jueves',9,17,'cursando').
ocupado('viernes',9,12,'cursando').
ocupado('lunes',17,18,'entrenando').
ocupado('miercoles',17,18,'entrenando').
ocupado('viernes',17,18,'entrenando').
ocupado(_,0,8,'durmiendo').
ocupado('sabado',0,12,'durmiendo').
ocupado('domingo',0,12,'durmiendo').
esta_ocupado(D,H,A):-ocupado(D,I,F,A),H >= I,H =< F.

actividades_dia(D,F):-ocupado(D,_,F,_).

conoce_acerca_de(N,T,X):-conoce(N,T,X).
conoce(5,'Inteligencia artificial','Es una disciplina que intenta hacer que una maquina sea igual o mas inteligente, teoricamente, que un humano').
conoce(1,'Agentes inteligentes','Son entidades capaces de percibir y responder a su entorno. Un ejemplo claro son los chatbot').
conoce(2,'Cambios guarani','Me parece que hay ciertas cosas que podrian mejorarse y agregarse').
conoce(3,'RoboCup','Es una competencia de futbol con robots autonomos jugando en equipo').
conoce(4,'Robots juegan futbol equipo','Hay una competencia de eso llamada RoboCup').

opina_sobre(X,Y,Z):-opinion(X,Y,Z).
opinion(2,2,'modificar la ventana de datos para que se muestre un resumen de los datos personales mas importantes').
opinion(2,3,'crear una nueva pestaña que englobe la agenda de clases, temas dictados por clase e historial de asistencias').
opinion(4,1,'Es muy interesante, esta buenisimo ver la evolucion de la robotica y la IA').
opinion(3,1,'Es muy interesante, esta buenisimo ver la evolucion de la robotica y la IA').
opinion(5,1,'Me parece re interesante, ademas dentro de muy poco va a estar en muchos mas aspectos de nuestra vida').
opinion(2,1,'que se pueda guardar la promocion de materias por un cierto tiempo y se acrediten automaticamente al rendirse las correlativas necesarias').

argumento_opinion(X,Y,Z):-argumento(X,Y,Z).
argumento(2,2,'algunos datos personales bastante requeridos, como por ejemplo el legajo universitario, son dificiles de acceder').
argumento(2,3,'facilitaria mucho el acceso a la informacion, y la haria mas amigable al usuario').
argumento(2,1,'actualmente esta tarea la hacen los profesores y resulta algo atrasada, ademas de ser bastante irregular en muchos casos. Ademas los alumnos tienen que llevar un registro manual del estado de sus promociones').