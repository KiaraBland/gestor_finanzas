from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required

ingresos = Blueprint("ingresos", __name__)

@ingresos.route('/ingresos')
@login_required
def index():
    ingresos = db.session.execute(text("SELECT * FROM ingresos WHERE usuario_id= :usuario_id"),{"usuario_id":session['usuario_id']}).fetchall()
    divisa=db.session.execute(text("SELECT * FROM divisa")).fetchall()
    categoria=db.session.execute(text("SELECT * FROM categoria")).fetchall()
    return render_template('Ingresos/index.html',ingresos=ingresos,divisa=divisa,categoria=categoria)

@categoria.route('/crearingresos',methods=["POST", "GET"])
@login_required
def ingresoscrear():
    
     if request.method == 'POST':
        # Capturar datos del formulario
        cantidad = request.form['cantidad']
      
        divisa = request.form['divisa']
        categoria = request.form['categoria']


        

        # Insertar el nuevo usuario en la base de datos
        db.session.execute(
            text("INSERT INTO ingresos (categoria_id,divisa_id,usuario_id,cantidad,fecha) VALUES (:categoria_id,:divisa_id,:usuario_id,:cantidad,:fecha)"),
            {"nombre": nombre, 
                "descripcion": descripcion}
        )
        db.session.commit()  # Confirmar cambios en la base de datos
        flash("Registro exitoso. .", "success")
        return redirect( url_for('categoria.index') )
    
