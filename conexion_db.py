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

def obtener_todos_Salas(filtro_columna='id_salon', orden='ASC', search=''):
    columnas_permitidas = ['id_salon', 'nombre_salon', 'ubicacion', 'cantidad_equipos', 'estado', 'descripcion', 'fecha_creacion', 'updated_at']
    if filtro_columna not in columnas_permitidas:
        filtro_columna = 'id_salon'
    orden = orden.upper()
    if orden not in ['ASC', 'DESC']:
        orden = 'ASC'

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT id_salon, nombre_salon, ubicacion, cantidad_equipos, estado, descripcion, fecha_creacion, updated_at
        FROM Salones
        WHERE 1=1
    """

    params = []
    if search:
        # si el search es un número, busca por ID; si no, por nombre
        if search.isdigit():
            query += " AND id_salon = %s"
            params.append(int(search))
        else:
            query += " AND nombre_salon LIKE %s"
            params.append(f"%{search}%")

    query += f" ORDER BY {filtro_columna} {orden}"

    cursor.execute(query, params)
    salones = cursor.fetchall()
    cursor.close()
    conn.close()
    return salones

def Sala_Existe(sala_id):
        conn = get_connection()
        cursor = conn.cursor()

        # Verificamos que la sala existe
        cursor.execute("SELECT id_salon FROM Salones WHERE id_salon = %s", (sala_id,))
        sala = cursor.fetchone()

        cursor.close()
        conn.close()
        return sala is not None
def eliminar_salon(sala_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Salones WHERE id_salon = %s", (sala_id,))
        
        conn.commit()
        cursor.close()
        conn.close()

# ===================== SALONES =====================

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
# ===================== OBTENER SALONES =====================

def obtener_Salones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Salones;")
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    return registros

# ===================== COMPUTADORAS =====================
def insertar_computadora(matricula, marca, sistema_operativo, estado="bueno",
                         fecha_adquisicion=None, id_pantalla=None,
                         id_teclado=None, id_mouse=None, id_salon=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Computadoras (
            matricula, marca, sistema_operativo, estado, fecha_adquisicion,
            id_pantalla, id_teclado, id_mouse, id_salon
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (matricula, marca, sistema_operativo, estado, fecha_adquisicion,
         id_pantalla, id_teclado, id_mouse, id_salon)
    )
    conn.commit()
    cursor.close()
    conn.close()

def existe_matricula(matricula):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_computadora FROM Computadoras WHERE matricula = %s", (matricula,))
    existe = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return existe

# ===================== MOUSE =====================
def insertar_mouse(marca, tipo="óptico", estado="operativa", foto=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Mouse (marca, tipo, estado, foto)
        VALUES (%s, %s, %s, %s)
        """,
        (marca, tipo, estado, foto)
    )
    mouse_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return mouse_id  # retornamos el id


# ===================== TECLADOS =====================
def insertar_teclado(marca, tipo="mecánico", estado="operativa", foto=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Teclados (marca, tipo, estado, foto)
        VALUES (%s, %s, %s, %s)
        """,
        (marca, tipo, estado, foto)
    )
    teclado_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return teclado_id  # retornamos el id


# ===================== PANTALLAS =====================
def insertar_pantalla(marca, estado="operativa", foto=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Pantallas (marca, estado, foto)
        VALUES (%s, %s, %s)
        """,
        (marca, estado, foto)
    )
    pantalla_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return pantalla_id  # retornamos el id

# ===================== OBTENER ID Y NOMBRE DE SALONES =====================

def obtener_id_y_nombre_salones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_salon, nombre_salon FROM Salones;")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def obtener_computadoras_con_sala_id(sala_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_computadora, id_mouse, id_teclado, id_pantalla FROM Computadoras WHERE id_salon = %s", (sala_id,))
    computadoras = cursor.fetchall()
    cursor.close()
    conn.close()
    return computadoras

def Cantidad_equipos(id_salon):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Salones SET cantidad_equipos = IFNULL(cantidad_equipos, 0) + 1 WHERE id_salon = %s",
        (id_salon,)
    )
    conn.commit()
    cursor.close()
    conn.close()

def obtener_todas_computadoras(filtro_columna='id_computadora', orden='ASC', search=''):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # Para acceder a los nombres de columnas

    # Query principal con LEFT JOIN a todos los componentes y Salones
    query = """
        SELECT 
            c.id_computadora,
            c.matricula,
            c.marca AS marca_pc,
            c.sistema_operativo,
            c.estado AS estado_pc,
            c.fecha_adquisicion,
            c.fecha_creacion AS fecha_creacion_pc,
            c.updated_at AS actualizado_pc,
            
            -- Datos del mouse
            m.id_mouse,
            m.marca AS marca_mouse,
            m.tipo AS tipo_mouse,
            m.estado AS estado_mouse,
            
            -- Datos del teclado
            t.id_teclado,
            t.marca AS marca_teclado,
            t.tipo AS tipo_teclado,
            t.estado AS estado_teclado,
            
            -- Datos de la pantalla
            p.id_pantalla,
            p.marca AS marca_pantalla,
            p.estado AS estado_pantalla,
            
            -- Datos del salón
            s.id_salon,
            s.nombre_salon
        FROM Computadoras c
        LEFT JOIN Mouse m ON c.id_mouse = m.id_mouse
        LEFT JOIN Teclados t ON c.id_teclado = t.id_teclado
        LEFT JOIN Pantallas p ON c.id_pantalla = p.id_pantalla
        INNER JOIN Salones s ON c.id_salon = s.id_salon
        WHERE 1=1
    """

    params = []
    if search:
        if search.isdigit():
            query += " AND c.id_computadora = %s"
            params.append(int(search))
        else:
            query += " AND (c.matricula LIKE %s OR c.marca LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

    # Validación de columna permitida
    columnas_permitidas = [
        'id_computadora', 'matricula', 'marca_pc', 'sistema_operativo', 
        'estado_pc', 'fecha_adquisicion', 'fecha_creacion_pc', 'actualizado_pc',
        'id_salon', 'nombre_salon'
    ]
    if filtro_columna not in columnas_permitidas:
        filtro_columna = 'id_computadora'

    # Mapear alias a columnas reales de la DB
    columnas_map = {
        'id_computadora': 'c.id_computadora',
        'matricula': 'c.matricula',
        'marca_pc': 'c.marca',
        'sistema_operativo': 'c.sistema_operativo',
        'estado_pc': 'c.estado',
        'fecha_adquisicion': 'c.fecha_adquisicion',
        'fecha_creacion_pc': 'c.fecha_creacion',
        'actualizado_pc': 'c.updated_at',
        'id_salon': 's.id_salon',
        'nombre_salon': 's.nombre_salon'
    }
    filtro_columna = columnas_map[filtro_columna]

    # Validar orden
    orden = orden.upper()
    if orden not in ['ASC', 'DESC']:
        orden = 'ASC'

    # Añadir ORDER BY
    query += f" ORDER BY {filtro_columna} {orden}"

    cursor.execute(query, params)
    computadoras = cursor.fetchall()
    cursor.close()
    conn.close()
    return computadoras



