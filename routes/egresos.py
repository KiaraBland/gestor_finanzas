from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required
import datetime


egresos = Blueprint("egresos", __name__)
@egresos.route('/egresos')
@login_required
def index():
    egresos = db.session.execute(
    text("""
        SELECT egresos.*, 
               Categoria.nombre AS categoria, divisa.nombre AS divisa, divisa.simbolo
        FROM egresos
        JOIN Categoria ON egresos.categoria_id = Categoria.id
        JOIN divisa ON egresos.divisa_id = divisa.id
        WHERE egresos.usuario_id = :usuario_id
    """),
    {"usuario_id": session['usuario_id']}
).fetchall()

    divisa=db.session.execute(text("SELECT * FROM divisa")).fetchall()
    categoria=db.session.execute(text("SELECT * FROM categoria WHERE tipo=0")).fetchall()
    return render_template('egresos/index.html',egresos=egresos,divisa=divisa,categoria=categoria)

@egresos.route('/crearegresos',methods=["POST", "GET"])
@login_required
def egresoscrear():
    
     if request.method == 'POST':
        # Capturar datos del formulario
        cantidad = request.form['cantidad']
        divisa = request.form['divisa']
        categoria = request.form['categoria']
        habitual= request.form['habitual']
        fecha_pago = request.form['fecha_pago']
        estado=request.form['estado']
   
        fecha = datetime.date.today()
        if not cantidad or not divisa or not categoria:
                flash("Todos los campos son obligatorios.", "error")
                return redirect(url_for('egresos.crearegresos'))
        # Insertar el nuevo usuario en la base de datos
        db.session.execute(
            text("INSERT INTO egresos (categoria_id,divisa_id,usuario_id,cantidad,habitual,fecha_pago,fecha,estado) VALUES (:categoria_id,:divisa_id,:usuario_id,:cantidad,:habitual,:fecha_pago,:fecha,:estado)"),
            {"categoria_id": categoria, 
                "divisa_id": divisa,
                "usuario_id":session['usuario_id'],
                "cantidad":cantidad,
                "habitual":habitual,
                "fecha_pago":fecha_pago,
                "fecha":fecha,
                "estado":estado
                }
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
                "tipo":"egreso"}
        )
        db.session.commit() 
         
        db.session.execute(
            text("INSERT INTO notificacion (usuario_id,descripcion,medio,visto) VALUES (:usuario_id,:descripcion,:medio,:visto)"),
            {"usuario_id":session['usuario_id'],
                "descripcion":"Se ha registrado un nuevo egreso con el concepto" + " " +concepto,
                "medio":"Nuevo egreso",
                "visto":0
            }
        )
        db.session.commit() 

        

        flash("Registro exitoso. .", "success")
        return redirect( url_for('egresos.index') )
    
@egresos.route('/actualizaregreso/<int:id>', methods=["POST", "GET"])
@login_required
def actualizar_egreso(id):
    # Recuperamos el egreso que vamos a editar
    egresos = db.session.execute(
        text("SELECT * FROM egresos WHERE id = :id"),
        {"id": id}
    ).fetchone()

    if not egresos:
        flash("Egreso no encontrado.", "error")
        return redirect(url_for('egresos.index'))

    if request.method == 'POST':
        # Capturamos los datos enviados en el formulario
        cantidad = request.form['cantidad']
        divisa = request.form['divisa']
        categoria = request.form['categoria']
        habitual= request.form['habitual']
        fecha_pago = request.form['fecha_pago']
        estado = request.form['estado']
        print(cantidad)
        # Validación de los campos
        if not cantidad or not divisa or not categoria:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('egresos.actualizaregreso', id=id))

        
        db.session.execute(
    text("""
        UPDATE egresos 
        SET 
            categoria_id = :categoria_id,
            divisa_id = :divisa_id,
            cantidad = :cantidad,
            habitual = :habitual,
            fecha_pago = :fecha_pago,
            estado = :estado
        WHERE id = :egreso_id
    """),
    {
        "categoria_id": categoria,
        "divisa_id": divisa,
        "usuario_id": session['usuario_id'],
        "cantidad": cantidad,
        "habitual": habitual,
        "fecha_pago": fecha_pago,
        "estado": estado,
        "egreso_id": id  # El identificador del egreso que deseas actualizar
    }
)
        db.session.commit()

        db.session.commit()  
        categorianombre=db.session.execute(
        text("SELECT * FROM categoria WHERE id = :id"),
        {"id": categoria}
    ).fetchone()
        
        concepto=categorianombre[1]
        db.session.execute(
            text("INSERT INTO notificacion (usuario_id,descripcion,medio,visto) VALUES (:usuario_id,:descripcion,:medio,:visto)"),
            {"usuario_id":session['usuario_id'],
                "descripcion":"Se ha registrado la actualizacion egreso con el concepto"+ " " +concepto,
                "medio":"Actualizacion egreso",
                "visto":0
            }
        )
        db.session.commit() 
        flash("Egreso actualizado exitosamente.", "success")
        return redirect(url_for('egresos.index'))
    
@egresos.route('/replicaregresos',methods=["POST", "GET"])
@login_required
def egresosreplicar():
    
     if request.method == 'POST':
        # Capturar datos del formulario
        cantidad = request.form['cantidad']
        divisa = request.form['divisa']
        categoria = request.form['categoria']
        habitual= request.form['habitual']
        fecha_pago = request.form['fecha_pago']
        estado = request.form['estado']
        fecha = datetime.date.today()
        if not cantidad or not divisa or not categoria:
                flash("Todos los campos son obligatorios.", "error")
                return redirect(url_for('egresos.crearegresos'))
        # Insertar el nuevo usuario en la base de datos
        db.session.execute(
            text("INSERT INTO egresos (categoria_id,divisa_id,usuario_id,cantidad,habitual,fecha_pago,fecha,estado) VALUES (:categoria_id,:divisa_id,:usuario_id,:cantidad,:habitual,:fecha_pago,:fecha,:estado)"),
            {"categoria_id": categoria, 
                "divisa_id": divisa,
                "usuario_id":session['usuario_id'],
                "cantidad":cantidad,
                "habitual":habitual,
                "fecha_pago":fecha_pago,
                "fecha":fecha,
                "estado":estado
                
                }
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
                "tipo":"egreso"}
        )
        db.session.commit() 
        
        
        db.session.execute(
            text("INSERT INTO notificacion (usuario_id,descripcion,medio,visto) VALUES (:usuario_id,:descripcion,:medio,:visto)"),
            {"usuario_id":session['usuario_id'],
                "descripcion":"Se ha registrado un nuevo egreso con el concepto" + " " +concepto,
                "medio":"Nuevo egreso",
                "visto":0
            }
        )
        db.session.commit() 


        flash("Registro replicado exitosamente. .", "success")
        return redirect( url_for('egresos.index') )


@egresos.route('/cancelaregreso/<int:id>', methods=['POST'])
@login_required
def cancelaregreso(id):

    egreso = db.session.execute(
            text("SELECT estado FROM egresos WHERE id = :id"),
            {"id": id}
        ).fetchone()

    if not egreso:
        flash("Egreso no encontrado.", "error")
        return redirect(url_for('egresos.index'))

        # Verificar que el egreso no esté ya cancelado
    if egreso[0] == 1:  # 1 es el estado de "Cancelado"
        flash("Este egreso ya está cancelado.", "warning")
        return redirect(url_for('egresos.index'))

        # Cambiar el estado a cancelado (0) usando SQL puro
    db.session.execute(
            text("UPDATE egresos SET estado = 1 WHERE id = :id"),
            {"id": id}
        )
    db.session.commit()
    flash("Egreso cancelado exitosamente.", "success")


    return redirect(url_for('egresos.index'))