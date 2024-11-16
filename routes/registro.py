from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required

usuarios = Blueprint("usuarios", __name__)


@usuarios.route('/usuarios')
@login_required
def index():
    usuarios = db.session.execute(text("SELECT * FROM usuarios")).fetchall()

    return render_template('index.html', usuarios=usuarios)

@usuarios.route('/perfil')
@login_required
def perfil():
    id=  session['usuario_id']
    usuarios = db.session.execute(text("SELECT * FROM usuarios WHERE id = :id"),
            {"id": id}
        ).fetchone()
    print(usuarios)

    return render_template('Layout/perfil.html',usuarios=usuarios)


@usuarios.route('/actualizar_perfil', methods=['POST'])
@login_required
def actualizar_perfil():
    usuario_id = session['usuario_id']
    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']
    
    # Verificar si el correo o teléfono ya existen en otros usuarios
    existente = db.session.execute(
        text("SELECT * FROM usuarios WHERE (correo = :correo OR telefono = :telefono) AND id != :id"),
        {"correo": correo, "telefono": telefono, "id": usuario_id}
    ).fetchone()
   

    # Si existe un usuario con el mismo correo o teléfono
    if existente:
        flash("El correo o teléfono ya están registrados por otro usuario.", "error")
        return redirect(url_for('categoria.index'))

    # Realizar la actualización si no existe ningún conflicto
    db.session.execute(
        text("UPDATE usuarios SET nombre = :nombre, correo = :correo, telefono = :telefono WHERE id = :id"),
        {"nombre": nombre, "correo": correo, "telefono": telefono, "id": usuario_id}
    )
    db.session.commit()

    flash("Perfil actualizado exitosamente.", "success")
    return redirect(url_for('categoria.index'))

@usuarios.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Capturar datos del formulario
        correo = request.form['correo']
        clave = request.form['clave']

        # Verificar si el usuario existe en la base de datos
        usuario = db.session.execute(
            text("SELECT * FROM usuarios WHERE correo = :correo"),
            {"correo": correo}
        ).fetchone()
        print(usuario)
        # Si el usuario existe y la contraseña coincide
        if usuario and check_password_hash(usuario[4], clave):
            # Iniciar sesión guardando datos en la sesión del usuario
            session['usuario_id'] = usuario[0]
            session['nombre'] = usuario[1]
            flash("Inicio de sesión exitoso. Bienvenido/a, " +
                  usuario[1], "success")
            return redirect(url_for('transacciones.index'))
        else:
            flash("Correo o contraseña incorrectos.", "error")
            return redirect(url_for('usuarios.login'))

    # Si es un método GET, renderizar el formulario de login
    return render_template('Login/login.html')


@usuarios.route('/auth/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Capturar datos del formulario
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']
        clave = request.form['clave']
        hash = generate_password_hash(clave)

        # Verificar si el usuario ya existe por correo o teléfono
        existente = db.session.execute(
            text("SELECT * FROM usuarios WHERE correo = :correo OR telefono = :telefono"),
            {"correo": correo, "telefono": telefono}
        ).fetchone()

        if existente:
            flash(
                "El correo o teléfono ya están registrados. Intente con otros datos.", "error")
            return redirect(url_for('usuarios.registro'))

        # Insertar el nuevo usuario en la base de datos
        db.session.execute(
            text("INSERT INTO usuarios (nombre, telefono, correo, clave) VALUES (:nombre, :telefono, :correo, :clave)"),
            {"nombre": nombre, "telefono": telefono,
                "correo": correo, "clave": hash}
        )
        db.session.commit()  # Confirmar cambios en la base de datos
        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for('usuarios.index'))

    # Si es un método GET, renderizar el formulario de registro
    return render_template('Login/registro.html')


@usuarios.route("/logout", methods=["POST", "GET"])
def logout():

    session.pop('usuario_id', None)
    # Redireccionar al inicio de sesión
    flash("Se ha cerrado la sesion correctamente", "success")
    return redirect(url_for('usuarios.login'))
