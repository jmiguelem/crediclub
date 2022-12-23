import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request
import requests

#SQL QUERIES
CREATE_TABLE = '''CREATE TABLE IF NOT EXISTS USERS(
	ID	SERIAL	PRIMARY KEY NOT NULL,
	PRIMER_NOMBRE	VARCHAR	NOT NULL,
	APELLIDO_PAT	VARCHAR	NOT NULL,
	APELLIDO_MAT	VARCHAR	NOT NULL,
	FECHA_NAC	DATE	NOT NULL,
	RFC	VARCHAR	NOT NULL,
	INGRESOS_MENSUALES	INT	NOT NULL,
	DEPENDIENTES	INT	NOT NULL,
	APROBADO	BOOLEAN	NOT NULL
);'''

INSERT_RECORDS = '''INSERT INTO USERS(PRIMER_NOMBRE, APELLIDO_PAT, APELLIDO_MAT, FECHA_NAC, RFC, INGRESOS_MENSUALES, DEPENDIENTES, APROBADO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING ID;'''

#FUNCIONES
def aprobarCredito(ingresosMensuales, numeroDependientes):
    if ingresosMensuales > 25000:
        return True
    elif ingresosMensuales <= 25000 and ingresosMensuales >= 15000 and numeroDependientes < 3:
        return True
    return False

def obtener_rfc(nombre, apellidoPaterno, apellidoMaterno, fechaNacimiento):
    rfc = ''
    rfc += apellidoPaterno[:2]
    rfc += apellidoMaterno[0]
    rfc += nombre[0]
    rfc += fechaNacimiento[-2:]
    rfc += fechaNacimiento[3:5]
    rfc += fechaNacimiento[:2]
    return rfc

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
sql_connection = psycopg2.connect(url)

@app.post("/api/datos")
def obtener_datos():
    #OBTENER DATOS
    data = request.get_json()

    nombre = data["Nombre"]
    apellidoPaterno = data["ApellidoPaterno"]
    apellidoMaterno = data["ApellidoMaterno"]
    fecha = data["FechaNacimiento"]
    fechaNacimiento = datetime.strptime(fecha, '%d-%m-%Y')
    ingresosMensuales = data["Ingresos"]
    dependientes = data["Dependientes"]

    #CALCULAR DATOS
    rfc = obtener_rfc(nombre, apellidoPaterno, apellidoMaterno,fecha)
    aprobado = aprobarCredito(ingresosMensuales, dependientes)

    #INSERTAR DATOS A DB
    with sql_connection:
        with sql_connection.cursor() as cursor:
            cursor.execute(CREATE_TABLE)
            cursor.execute(INSERT_RECORDS, (nombre, apellidoPaterno, apellidoMaterno, fechaNacimiento, rfc, ingresosMensuales, dependientes, aprobado,))
            id = cursor.fetchone()[0]
    return {"ID":id, "RFC":rfc, "creditoAprobado":aprobado}
