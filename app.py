from flask import Flask,jsonify,request,render_template
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_CONNECTION_URI
from utils.db import db
from routes.registro import usuarios
from routes.Ingresos import ingresos
from routes.egresos import egresos 
from routes.categoria import categoria
 
import logging
app = Flask(__name__)

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
def index():
    return render_template('Layout/base.html')

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
app.register_blueprint(categoria)


