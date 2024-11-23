from flask import Flask,jsonify,request,render_template,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_CONNECTION_URI
from utils.db import db
from routes.registro import usuarios
from routes.Ingresos import ingresos
from routes.egresos import egresos  
from routes.transacciones import transacciones  
from routes.asistente import asistente 
from routes.categoria import categoria
from utils.helper import login_required
import logging
from dotenv import load_dotenv
import os
from sqlalchemy import text
from flask_mail import Mail, Message
from datetime import datetime, timedelta
load_dotenv()
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app = Flask(__name__)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ["GMAIL_EMAIL"]  # Use your actual Gmail address
app.config['MAIL_PASSWORD'] = os.environ["GMAIL_PASSWORD"]     # Use your generated App Password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)



# settings
app.secret_key = '12345678'
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['MYSQL_SSL_DISABLED'] = True
 
# no cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
db.init_app(app) 

# Configuración del registro
logging.basicConfig(level=logging.INFO)



@app.route('/')
@login_required
def index():
    return redirect(url_for('transacciones.index'))

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': 'The requested resource was not found on the server.'}), 404

@app.after_request
def after_request(response):
    # Agregar encabezados de CORS (Cross-Origin Resource Sharing)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    
    # Puedes registrar información sobre la solicitud
    app.logger.info(f"Request: {request.method} {request.path} - Response Status: {response.status}")
    
    return response
def obtener_pagos_pendientes():
    # Obtener la fecha de mañana
    manana = datetime.now() + timedelta(days=1)
    manana_str = manana.strftime('%Y-%m-%d')  # Formato de fecha en formato ISO (yyyy-mm-dd)

    # Consulta para obtener los pagos pendientes para el día de mañana
    result = db.session.execute(
        text("""
            SELECT * FROM egresos 
            WHERE DATE(fecha_pago) = :fecha_pago AND estado = 'pendiente'
        """),
        {"fecha_pago": manana_str}
    ).fetchall()
    return result

def verificar_recordatorio_existente(usuario_id):
    mañana = datetime.now() + timedelta(days=1)
    mañana_str = mañana.strftime('%Y-%m-%d')

    # Verificar si ya existe un recordatorio de pago pendiente para mañana
    result = db.session.execute(
        text("""
            SELECT COUNT(*) FROM notificacion 
            WHERE usuario_id = :usuario_id 
            AND medio = 'Recordatorio de pago' 
            AND descripcion LIKE :descripcion
        """),
        {"usuario_id": usuario_id, "descripcion": f"%{mañana_str}%"}
    ).fetchone()

    return result[0] > 0  



# Función para crear el recordatorio en la base de datos
def crear_recordatorio(usuario_id):
    manana = datetime.now() + timedelta(days=1)
    manana_str = manana.strftime('%Y-%m-%d')

    descripcion = f"Recordatorio de pagos pendientes para mañana ({manana_str})"
    
    db.session.execute(
        text("""
            INSERT INTO notificacion (usuario_id, descripcion, medio, visto) 
            VALUES (:usuario_id, :descripcion, 'Recordatorio de pago', 0)
        """),
        {"usuario_id": usuario_id, "descripcion": descripcion}
    )
    db.session.commit()

# El contexto de notificaciones y recordatorios
@app.context_processor
def inject_notificaciones():
    def contar_notificaciones_no_vistas(usuario_id):
        result = db.session.execute(
            text("SELECT COUNT(*) FROM notificacion WHERE usuario_id = :usuario_id AND visto = 0"),
            {"usuario_id": usuario_id}
        ).fetchone()
        return result[0] if result else 0

    def obtener_medios_unicos_no_vistos(usuario_id):
        result = db.session.execute(
            text("SELECT DISTINCT medio FROM notificacion WHERE usuario_id = :usuario_id AND visto = 0"),
            {"usuario_id": usuario_id}
        ).fetchall()
        return [row[0] for row in result]

    # Obtener el usuario actual desde la sesión
    usuario_id = session.get('usuario_id', None)

    if usuario_id:
        # Verificar si ya se ha enviado el recordatorio
        if not verificar_recordatorio_existente(usuario_id):
           
            crear_recordatorio(usuario_id)

    notificaciones_no_vistas = contar_notificaciones_no_vistas(usuario_id) if usuario_id else 0
    medios_unicos_no_vistos = obtener_medios_unicos_no_vistos(usuario_id) if usuario_id else []

    return {
        'notificaciones_no_vistas': notificaciones_no_vistas,
        'medios_unicos_no_vistos': medios_unicos_no_vistos
    }

app.register_blueprint(usuarios)
app.register_blueprint(ingresos)
app.register_blueprint(egresos)
app.register_blueprint(transacciones)
app.register_blueprint(categoria)
app.register_blueprint(asistente)



           


