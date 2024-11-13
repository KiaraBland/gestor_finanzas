from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required

transacciones = Blueprint("transacciones", __name__)


@transacciones.route('/inicio')
@login_required
def index():
    ingresosencordobas = db.session.execute(text("SELECT sum(cantidad) as cantidad FROM ingresos where divisa_id = 1 and usuario_id=:usuario_id"),{"usuario_id": session['usuario_id']}).fetchone()
    ingresosendolar = db.session.execute(text("SELECT sum(cantidad) as cantidad FROM ingresos where divisa_id = 2 and usuario_id=:usuario_id"),{"usuario_id": session['usuario_id']}).fetchone()
    egresosencordobas = db.session.execute(text("SELECT sum(cantidad) as cantidad FROM egresos where divisa_id = 1 and usuario_id=:usuario_id"),{"usuario_id": session['usuario_id']}).fetchone()
    egresosendolares = db.session.execute(text("SELECT sum(cantidad) as cantidad FROM egresos where divisa_id = 2 and usuario_id=:usuario_id"),{"usuario_id": session['usuario_id']}).fetchone()
    print(ingresosencordobas)
    #saldototalencordoba=int(ingresosencordobas["cantidad"])-int(egresosencordobas["cantidad"])
    saldototalencordoba=0
    return render_template('index.html',ingresosencordobas=ingresosencordobas, ingresosendolar=ingresosendolar, egresosencordobas=egresosencordobas, egresosendolares=egresosendolares, saldototalencordoba= saldototalencordoba)