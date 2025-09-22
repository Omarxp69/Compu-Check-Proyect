import mysql.connector
import os
from dotenv import load_dotenv
# Cargar variables de entorno
# load_dotenv()
# def get_connection():
#     conexion = mysql.connector.connect(
#         host=os.environ.get('MYSQLHOST'),
#         user=os.environ.get('MYSQLUSER'),
#         password=os.environ.get('MYSQLPASSWORD'),
#         database=os.environ.get('MYSQLDATABASE'),
#         port=int(os.environ.get('MYSQLPORT', 3306)),
#     )
#     return conexion

def get_connection():
    conexion = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Guada_xp69@3',
        database='pythonflask'
    )
    return conexion


def insertar_usuario(nombre, apellido_paterno, apellido_materno, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (nombre, apellido_paterno, apellido_materno, email, password)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (nombre, apellido_paterno, apellido_materno, email, password)
    )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_todos_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users;")
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    return registros


def obtener_usuario_por_email(email):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND estado = 1", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user

