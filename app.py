from config import config
from validaciones import correo_valido, contrasena_valida 
from conexion_db import *
from flask import Flask,render_template,make_response,redirect,request,flash,url_for,session
import bcrypt
from conexion_db import obtener_usuario_por_email, insertar_usuario, get_connection,agregar_salon, obtener_Salones,obtener_todos_usuarios
from functools import wraps
import os
from dotenv import load_dotenv
import os
load_dotenv()
from werkzeug.utils import secure_filename
import glob 


app=Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



ROLE_DASHBOARDS = {
    'admin': 'dashboard',
    'moderador': 'dashboard',
    'user': 'dashboard'
}
def role_required(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                flash("❌ Debes iniciar sesión")
                return redirect(url_for('login'))
            if session['role'] not in roles_permitidos:
                flash("❌ Acceso denegado")
                # Redirige al dashboard según su rol si no tiene permisos
                return redirect(url_for(ROLE_DASHBOARDS.get(session['role'], 'index')))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decorador para rutas de login/registro, evita que usuarios logueados accedan
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' in session:
            # Redirige al dashboard correspondiente según rol
            return redirect(url_for(ROLE_DASHBOARDS.get(session['role'], 'index')))
        return f(*args, **kwargs)
    return decorated_function


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/")
@logout_required
def index():
    return render_template('inicio.html')
    

@app.route("/login", methods=["GET", "POST"])
@logout_required
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash("❌ Debes llenar todos los campos")
            return redirect(url_for('login'))
        
        user=obtener_usuario_por_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user[5].encode()):
            session['nombre'] = user[1]  # username
            session['email']=user[4]     #email
            session['role'] = user[9]    # role
            session['user_id'] = user[0]
            session.permanent = True
            flash("✅ Login exitoso")
            #return redirect(url_for(ROLE_DASHBOARDS.get(user[9], 'index')))
            return redirect(url_for('dashboard'))
        else:
            flash("❌ Login fallido")
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
@logout_required
def register():
    if request.method == "POST":
        # Leer datos del formulario
        apellido_paterno = request.form.get('apellido_paterno')
        apellido_materno = request.form.get('apellido_materno')
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # Validaciones
        if not correo_valido(email):
            flash("❌ Correo no válido")
            return redirect(url_for('register'))
        if obtener_usuario_por_email(email):
            flash("❌ El correo ya está registrado")
            return redirect(url_for('register'))
        if not contrasena_valida(password):
            flash("❌ La contraseña debe tener mínimo 8 caracteres, una letra mayúscula, un número")
            return redirect(url_for('register'))
        if password != confirm_password:
            flash("❌ Las contraseñas no coinciden")
            return redirect(url_for('register'))
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()
        insertar_usuario(nombre,apellido_paterno,apellido_materno,email,hashed_password)
        flash("✅ Registro exitoso. Ahora puedes iniciar sesión.")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("✅ Has cerrado sesión correctamente")
    return redirect(url_for('index'))

def get_current_user():
    email = session.get('email')
    if not email:
        return None  # Usuario no logueado
    user = obtener_usuario_por_email(email)  # Trae todos los datos de la DB
    #print(user)
    if not user:
        return None  # Usuario no encontrado en la DB

    return {
        'id': user[0],
        'name': user[1],
        'apellido_paterno': user[2],
        'apellido_materno': user[3],
        'email': user[4],
        'role': user[9],  # Ajusta según la posición del rol en tu tabla
        'foto_perfil':user[6]
    }

@app.route('/dashboard')
@role_required('admin', 'moderador', 'user')
def dashboard():
    user = get_current_user()
    if not user:
        flash("❌ Debes iniciar sesión")
        return redirect(url_for('login'))
    user_name=user['name'].capitalize()
    user_role=user['role']
    user_profile_pic=user['foto_perfil']

    return render_template('dashboard.html',user_name=user_name,user_role=user_role,user_profile_pic=user_profile_pic)


@app.route('/update_profile', methods=['POST'])
@role_required('admin', 'moderador', 'user')
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("⚠️ Debes iniciar sesión.")
        return redirect(url_for('login'))

    db = get_connection()
    cursor = db.cursor()

    updated = False

    # --- FOTO DE PERFIL ---
    file = request.files.get('foto_perfil')
    if file and allowed_file(file.filename):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        pattern = os.path.join(app.config['UPLOAD_FOLDER'], f"user_{user_id}.*")
        for old_file in glob.glob(pattern):
            try:
                os.remove(old_file)
            except OSError:
                pass

        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"user_{user_id}.{extension}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        relative_path = f"uploads/{filename}"
        cursor.execute("UPDATE users SET foto_perfil = %s WHERE id = %s", (relative_path, user_id))
        flash("✅ Foto de perfil actualizada.")
        updated = True

    # --- FECHA DE NACIMIENTO ---
    fecha = request.form.get("fecha_nacimiento")
    if fecha:
        cursor.execute("UPDATE users SET fecha_nacimiento = %s WHERE id = %s", (fecha, user_id))
        flash("✅ Fecha de nacimiento actualizada.")
        updated = True

    # --- GÉNERO ---
    genero = request.form.get("genero")
    if genero:
        cursor.execute("UPDATE users SET genero = %s WHERE id = %s", (genero, user_id))
        flash("✅ Género actualizado.")
        updated = True
    if updated:
        db.commit()
    cursor.close()
    db.close()
    # Nunca redirijas a login, siempre al dashboard
    return redirect(url_for('dashboard'))

@app.route('/delete_account', methods=['POST'])
@role_required('admin', 'moderador', 'user')
def delete_account():
    user_id = session.get("user_id")
    if not user_id:
        flash("⚠️ Debes iniciar sesión para eliminar tu cuenta.")
        return redirect(url_for('login'))
    db = get_connection()
    cursor = db.cursor()
    # Cambiar estado a 0 (inactivo)
    cursor.execute("UPDATE users SET estado = 0 WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    db.close()
    # Limpiar sesión
    session.clear()
    flash("✅ Tu cuenta ha sido desactivada. Puedes reactivarla más tarde.")
    return redirect(url_for('index'))



@app.route('/profile')
@role_required('admin', 'moderador', 'user')
def perfil():
    user = get_current_user()
    user_name=user['name'].capitalize()
    user_role=user['role']
    user_profile_pic=user['foto_perfil']

    return render_template('profile.html',user_name=user_name,user_profile_pic=user_profile_pic,user_role=user_role)

# aqui se crearan salas, eliminiran salas , mostraran salas
@app.route('/Salas', methods=['GET', 'POST'])
@role_required('admin')
def salas():
    user = get_current_user()
    user_name=user['name'].capitalize()
    user_role=user['role']
    user_profile_pic=user['foto_perfil']

    if request.method == 'POST':
        nombre_salon = request.form['nombre_salon'].strip()
        ubicacion = request.form['ubicacion'].strip()
        estado = request.form['estado'].strip()
        descripcion = request.form['descripcion'].strip() 

        # Validaciones básicas
        #si el nombre de la sala esta vacio o es muy largo
        if not nombre_salon or len(nombre_salon) > 100:
            flash("❌ El nombre de la sala es inválido.")
            return render_template('salas.html', user_name=user_name, user_role=user_role, user_profile_pic=user_profile_pic)
        #si la ubicacion esta vacia o es muy larga
        if not ubicacion or len(ubicacion) > 150:
            flash("❌ La ubicación es inválida.")
            return render_template('salas.html', user_name=user_name, user_role=user_role, user_profile_pic=user_profile_pic)
        #si el estado no es uno de los permitidos
        if estado not in ('activo','mantenimiento','fuera de servicio'):
            flash("❌ Estado no válido.")
            return render_template('salas.html', user_name=user_name, user_role=user_role, user_profile_pic=user_profile_pic)
        #si la descripcion es muy larga
        if len(descripcion) > 500:  # opcional, límite de caracteres
            flash("❌ La descripción es demasiado larga.")
            return render_template('salas.html', user_name=user_name, user_role=user_role, user_profile_pic=user_profile_pic)
        agregar_salon(nombre_salon, ubicacion, estado, descripcion)
        flash("✅ Sala agregada exitosamente.")
    return render_template('salas.html',user_name=user_name,user_role=user_role,user_profile_pic=user_profile_pic)




@app.route('/Gestionar_Usuarios', methods=['GET', 'POST'])
@role_required('admin', 'moderador')
def gestionar_usuarios():


    user = get_current_user()
    user_name = user['name'].capitalize()
    user_role = user['role']
    user_profile_pic = user['foto_perfil']

    # Leer parámetros de filtro desde GET
    filtro_columna = request.args.get('filtro_columna', 'id')
    orden = request.args.get('orden', 'ASC')
    search = request.args.get('search', '').strip()  # nuevo parámetro de búsqueda

    usuarios = obtener_todos_usuarios(filtro_columna=filtro_columna, orden=orden, search=search)

    return render_template('Gestionar_Usuarios.html',
        user_name=user_name,
        user_role=user_role,
        user_profile_pic=user_profile_pic,
        usuarios=usuarios,
        filtro_columna=filtro_columna,
        orden=orden,
        search=search
    )

@app.route('/actualizar_usuario', methods=['POST'])
@role_required('admin')
def actualizar_usuario():
    user_id = request.form.get('user_id')
    nuevo_rol = request.form.get('rol')
    nuevo_estado = request.form.get('estado')
    admin_password = request.form.get('admin_password')

    if not admin_password:
        flash("❌ Debes ingresar tu contraseña para cambiar el rol.")
        return redirect(url_for('gestionar_usuarios'))

    # Verificar contraseña del admin
    admin = get_current_user()
    if not bcrypt.checkpw(admin_password.encode('utf-8'), obtener_usuario_por_email(admin['email'])[5].encode()):
        flash("❌ Contraseña incorrecta.")
        return redirect(url_for('gestionar_usuarios'))

    # Actualizar rol y estado en la base de datos
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET rol=%s, estado=%s WHERE id=%s", (nuevo_rol, nuevo_estado, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Usuario actualizado correctamente.")
    return redirect(url_for('gestionar_usuarios'))


@app.route('/Gestionar_Salas', methods=['GET', 'POST'])
@role_required('admin', 'moderador')
def gestionar_salas():


    user = get_current_user()
    user_name = user['name'].capitalize()
    user_role = user['role']
    user_profile_pic = user['foto_perfil']

    # Leer parámetros de filtro desde GET
    filtro_columna = request.args.get('filtro_columna', 'id')
    orden = request.args.get('orden', 'ASC')
    search = request.args.get('search', '').strip()  # nuevo parámetro de búsqueda

    usuarios = obtener_todos_usuarios(filtro_columna=filtro_columna, orden=orden, search=search)

    return render_template('Gestionar_Salas.html',
        user_name=user_name,
        user_role=user_role,
        user_profile_pic=user_profile_pic,
        usuarios=usuarios,
        filtro_columna=filtro_columna,
        orden=orden,
        search=search
    )














if __name__ == "__main__":
    app.config.from_object(config['development'])
    app.run()
