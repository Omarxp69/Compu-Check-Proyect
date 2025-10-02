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

def obtener_todos_usuarios(filtro_columna='id', orden='ASC', search=''):
    columnas_permitidas = ['id', 'nombre', 'apellido_paterno', 'apellido_materno', 'email', 'rol','estado','created_at','updated_at']
    if filtro_columna not in columnas_permitidas:
        filtro_columna = 'id'
    orden = orden.upper()
    if orden not in ['ASC', 'DESC']:
        orden = 'ASC'

    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT id, nombre, apellido_paterno, apellido_materno, email, rol, foto_perfil, estado, created_at, updated_at
        FROM users
        WHERE 1=1
    """

    params = []
    if search:
        # si el search es un número, busca por ID; si no, por email
        if search.isdigit():
            query += " AND id = %s"
            params.append(int(search))
        else:
            query += " AND email LIKE %s"
            params.append(f"%{search}%")

    query += f" ORDER BY {filtro_columna} {orden}"
    cursor.execute(query, params)
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios

def obtener_usuario_por_email(email):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND estado = 1", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user

def obtener_todos_Salas(filtro_columna='id', orden='ASC', search=''):
    columnas_permitidas = ['id', 'nombre_salon', 'ubicacion', 'cantidad_equipos', 'descripcion']
    if filtro_columna not in columnas_permitidas:
        filtro_columna = 'id'
    orden = orden.upper()
    if orden not in ['ASC', 'DESC']:
        orden = 'ASC'

    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT id, nombre, apellido_paterno, apellido_materno, email, rol, foto_perfil, estado
        FROM users
        WHERE 1=1
    """

    params = []
    if search:
        # si el search es un número, busca por ID; si no, por email
        if search.isdigit():
            query += " AND id = %s"
            params.append(int(search))
        else:
            query += " AND email LIKE %s"
            params.append(f"%{search}%")

    query += f" ORDER BY {filtro_columna} {orden}"
    cursor.execute(query, params)
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios


















def agregar_salon(nombre_salon, ubicacion, estado, descripcion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Salones (nombre_salon, ubicacion, estado, descripcion)
        VALUES (%s, %s, %s, %s)
        """,
        (nombre_salon, ubicacion, estado, descripcion)
    )
    conn.commit()
    cursor.close()
    conn.close()

def obtener_Salones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Salones;")
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    return registros


