from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required

categoria = Blueprint("categoria", __name__)


@categoria.route('/categoria')
@login_required
def index():
    
    categoria = db.session.execute(
            text("SELECT * FROM categoria")
        ).fetchall()
    print(categoria)
    return render_template('categoria/index.html',categoria=categoria)

@categoria.route('/crearcategoria',methods=["POST", "GET"])
@login_required
def categoriacrear():
    
     if request.method == 'POST':
        # Capturar datos del formulario
        nombre = request.form['nombre']
      
        descripcion = request.form['descripcion']


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
            text("INSERT INTO categoria (nombre, descripcion) VALUES (:nombre, :descripcion)"),
            {"nombre": nombre, 
                "descripcion": descripcion}
        )
        db.session.commit()  # Confirmar cambios en la base de datos
        flash("Registro exitoso. .", "success")
        return redirect( url_for('categoria.index') )
    