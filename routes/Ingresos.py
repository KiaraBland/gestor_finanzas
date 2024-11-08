from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required

ingresos = Blueprint("ingresos", __name__)


@ingresos.route('/ingresos')
@login_required
def index():
    usuarios = db.session.execute(text("SELECT * FROM usuarios")).fetchall()
   
    return render_template('index.html',usuarios=usuarios)


