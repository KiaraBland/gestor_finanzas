from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required
import datetime
ingresos = Blueprint("ingresos", __name__)

@ingresos.route('/ingresos')
@login_required
def index():
    ingresos = db.session.execute(
    text("""
        SELECT ingresos.*, 
               Categoria.nombre AS categoria, divisa.nombre AS divisa, divisa.simbolo
        FROM ingresos
        JOIN Categoria ON ingresos.categoria_id = Categoria.id
        JOIN divisa ON ingresos.divisa_id = divisa.id
        WHERE ingresos.usuario_id = :usuario_id
    """),
    {"usuario_id": session['usuario_id']}
).fetchall()

    divisa=db.session.execute(text("SELECT * FROM divisa")).fetchall()
    categoria=db.session.execute(text("SELECT * FROM categoria WHERE tipo=1")).fetchall()
    return render_template('Ingresos/index.html',ingresos=ingresos,divisa=divisa,categoria=categoria)

@ingresos.route('/crearingresos',methods=["POST", "GET"])
@login_required
def ingresoscrear():
    
     if request.method == 'POST':
        # Capturar datos del formulario
        cantidad = request.form['cantidad']
        divisa = request.form['divisa']
        categoria = request.form['categoria']
        fecha = datetime.date.today()
        if not cantidad or not divisa or not categoria:
                flash("Todos los campos son obligatorios.", "error")
                return redirect(url_for('ingresos.crearingresos'))
        # Insertar el nuevo usuario en la base de datos
        db.session.execute(
            text("INSERT INTO ingresos (categoria_id,divisa_id,usuario_id,cantidad,fecha) VALUES (:categoria_id,:divisa_id,:usuario_id,:cantidad,:fecha)"),
            {"categoria_id": categoria, 
                "divisa_id": divisa,
                "usuario_id":session['usuario_id'],
                "cantidad":cantidad,
                "fecha":fecha}
        )
        db.session.commit()  # Confirmar cambios en la base de datos

        categorianombre=db.session.execute(
        text("SELECT * FROM categoria WHERE id = :id"),
        {"id": categoria}
    ).fetchone()
        
        concepto=categorianombre[1]
        db.session.execute(
            text("INSERT INTO movimientos (usuario_id,divisa_id,cantidad,concepto,tipo) VALUES (:usuario_id,:divisa_id,:cantidad,:concepto,:tipo)"),
            {"usuario_id":session['usuario_id'],
                "divisa_id":divisa,
                "cantidad":cantidad,
                "concepto":concepto,
                "tipo":"ingreso"}
        )
        db.session.commit() 
         
        db.session.execute(
            text("INSERT INTO notificacion (usuario_id,descripcion,medio) VALUES (:usuario_id,:descripcion,:medio)"),
            {"usuario_id":session['usuario_id'],
                "descripcion":"Se ha registrado un nuevo ingreso con el concepto" + concepto,
                "medio":"Nuevo ingreso"
            }
        )
        db.session.commit() 

        flash("Registro exitoso. .", "success")
        return redirect( url_for('ingresos.index') )
    
@ingresos.route('/actualizaringreso/<int:id>', methods=["POST", "GET"])
@login_required
def actualizar_ingreso(id):
    # Recuperamos el ingreso que vamos a editar
    ingreso = db.session.execute(
        text("SELECT * FROM ingresos WHERE id = :id"),
        {"id": id}
    ).fetchone()

    if not ingreso:
        flash("Ingreso no encontrado.", "error")
        return redirect(url_for('ingresos.index'))

    if request.method == 'POST':
        # Capturamos los datos enviados en el formulario
        cantidad = request.form['cantidad']
        divisa = request.form['divisa']
        categoria = request.form['categoria']

        # Validación de los campos
        if not cantidad or not divisa or not categoria:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('ingresos.actualizaringreso', id=id))

        
        db.session.execute(
            text("""
                UPDATE ingresos
                SET categoria_id = :categoria_id, divisa_id = :divisa_id, cantidad = :cantidad
                WHERE id = :id
            """),
            {
                "categoria_id": categoria,
                "divisa_id": divisa,
                "cantidad": cantidad,
                "id": id
            }
        )
        db.session.commit()  
        categorianombre=db.session.execute(
        text("SELECT * FROM categoria WHERE id = :id"),
        {"id": categoria}
    ).fetchone()
        
        concepto=categorianombre[1]
         
        db.session.execute(
            text("INSERT INTO notificacion (usuario_id,descripcion,medio) VALUES (:usuario_id,:descripcion,:medio)"),
            {"usuario_id":session['usuario_id'],
                "descripcion":"Se ha actualizado el ingreso con el concepto" + concepto,
                "medio":"Actualización de egreso"
            }
        )
        db.session.commit() 

        flash("Ingreso actualizado exitosamente.", "success")
        return redirect(url_for('ingresos.index'))
    
@ingresos.route('/replicaringreso/<int:ingreso_id>', methods=["GET"])
@login_required
def replicaringreso(ingreso_id):
    # Fetch the original income entry by ID
    original_ingreso = db.session.execute(
        text("SELECT categoria_id, divisa_id, usuario_id, cantidad FROM ingresos WHERE id = :ingreso_id"),
        {"ingreso_id": ingreso_id}
    ).fetchone()

    if original_ingreso is None:
        flash("Ingreso no encontrado.", "error")
        return redirect(url_for('ingresos.index'))

    # Replicate the income entry with the current date
    fecha = datetime.date.today()
    db.session.execute(
        text("INSERT INTO ingresos (categoria_id, divisa_id, usuario_id, cantidad, fecha) VALUES (:categoria_id, :divisa_id, :usuario_id, :cantidad, :fecha)"),
        {
            "categoria_id": original_ingreso[0],  # Access by index
            "divisa_id": original_ingreso[1],
            "usuario_id": original_ingreso[2],
            "cantidad": original_ingreso[3],
            "fecha": fecha
        }
    )
    db.session.commit()  # Confirm the changes in the database1
    cantidad = request.form['cantidad']
    divisa = request.form['divisa']
    categoria = request.form['categoria']
    fecha = datetime.date.today()
    categorianombre=db.session.execute(
        text("SELECT * FROM categoria WHERE id = :id"),
        {"id": categoria}
    ).fetchone()
        
    concepto=categorianombre[1]
    db.session.execute(
            text("INSERT INTO movimientos (usuario_id,divisa_id,cantidad,concepto,tipo) VALUES (:usuario_id,:divisa_id,:cantidad,:concepto,:tipo)"),
            {"usuario_id":session['usuario_id'],
                "divisa_id":divisa,
                "cantidad":cantidad,
                "concepto":concepto,
                "tipo":"ingreso"}
        )
    db.session.commit() 
    db.session.execute(
            text("INSERT INTO notificacion (usuario_id,descripcion,medio) VALUES (:usuario_id,:descripcion,:medio)"),
            {"usuario_id":session['usuario_id'],
                "descripcion":"Se ha registrado un nuevo ingreso con el concepto" + concepto,
                "medio":"Nuevo ingreso"
            }
        )
    db.session.commit() 

    flash("Ingreso replicado exitosamente.", "success")


    
    return redirect(url_for('ingresos.index'))
