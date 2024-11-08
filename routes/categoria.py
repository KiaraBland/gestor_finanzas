from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required

categoria = Blueprint("categoria", __name__)


@categoria.route('/categoria')

def index():
    #usuarios = db.session.execute(text("SELECT * FROM usuarios")).fetchall()
   
    return render_template('Layout/base.html')

