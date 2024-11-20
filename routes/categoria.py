from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required

categoria = Blueprint("categoria", __name__)


@categoria.route('/categoria')
@login_required
def index():
    id=  session['usuario_id']
    usuarios = db.session.execute(text("SELECT * FROM usuarios WHERE id = :id"),
            {"id": id}
        ).fetchone()
    categoria = db.session.execute(
            text("SELECT * FROM categoria")
        ).fetchall()
    print(categoria)
    return render_template('categoria/index.html',categoria=categoria,usuarios=usuarios)

@categoria.route('/crearcategoria',methods=["POST", "GET"])
@login_required
def categoriacrear():
    
     if request.method == 'POST':
        # Capturar datos del formulario
        nombre = request.form['nombre']
      
        descripcion = request.form['descripcion']
        tipo= request.form['habitual']
        # Verificar si la categoria ya existe por el nombre
        existente = db.session.execute(
            text("SELECT * FROM categoria WHERE nombre = :nombre"),
            {"nombre": nombre}
        ).fetchone()

        if existente:
            flash(
                "El nombre y la categoria ya estan registrados. Intente con otros datos.", "error")
            return redirect(url_for('categoria.index'))

        # Insertar el nuevo usuario en la base de datos
        db.session.execute(
            text("INSERT INTO categoria (nombre, descripcion,tipo) VALUES (:nombre, :descripcion,:tipo)"),
            {"nombre": nombre, 
                "descripcion": descripcion,
                    "tipo": tipo}
        )
        db.session.commit()  # Confirmar cambios en la base de datos
        flash("Registro exitoso. .", "success")
        return redirect( url_for('categoria.index') )
    

@categoria.route('/actualizarcategoria/<int:id>', methods=["POST", "GET"])
@login_required
def actualizar_categoria(id):
    # Recuperamos el egreso que vamos a editar
    categoria = db.session.execute(
        text("SELECT * FROM categoria WHERE id = :id"),
        {"id": id}
    ).fetchone()

    if not categoria:
        flash("Categoria no encontrado.", "error")
        return redirect(url_for('categoria.index'))

    if request.method == 'POST':
        # Capturamos los datos enviados en el formulario
        nombre= request.form['nombre']
        descripcion = request.form['descripcion']
        
        # Validación de los campos
        
        
        db.session.execute(
            text("""
                UPDATE categoria
                SET nombre= :nombre, descripcion= :descripcion 
                WHERE id = :id
            """),
            {
                "nombre": nombre,
                "descripcion": descripcion,
                "id": id
            }
        )
        db.session.commit()  

        flash("Categoria actualizada exitosamente.", "success")
        return redirect(url_for('categoria.index'))

