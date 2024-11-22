from flask import Flask,jsonify,request,render_template,redirect,url_for
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
from flask_mail import Mail, Message
load_dotenv()

app = Flask(__name__)

#configuracion de envio de correo 
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']= 587
app.config['MAIL_USERNAME']= os.environ["GMAIL_EMAIL"]
app.config['MAIL_PASSWORD']= os.environ["GMAIL_PASSWORD"]
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USE_SSL']= False
app.config['MAIL_DEFAULT_SENDER']= 'smtp,gmail.com'


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
mail = Mail(app)

@app.route("/correo")
def correo():
    msg = Message(
        subject='Hello from the other side!', 
        sender= os.environ["GMAIL_EMAIL"],  # Ensure this matches MAIL_USERNAME
        recipients=['kiarablandon75@gmail.com']  # Replace with actual recipient's email
    )
    msg.body = "Hey, sending you this email from my Flask app, let me know if it works."
    mail.send(msg)
    return "Message sent!"
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

app.register_blueprint(usuarios)
app.register_blueprint(ingresos)
app.register_blueprint(egresos)
app.register_blueprint(transacciones)
app.register_blueprint(categoria)
app.register_blueprint(asistente)



           


