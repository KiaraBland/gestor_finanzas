from flask import Blueprint, render_template, request, redirect, url_for, flash,session,jsonify
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
    # Obtener valores con un valor predeterminado en caso de None
    ingresos_cordobas = ingresosencordobas[0] or 0
    egresos_cordobas = egresosencordobas[0] or 0
    ingresos_dolares = ingresosendolar[0] or 0
    egresos_dolares = egresosendolares[0] or 0

    
    
    # Calcular el saldo total en córdobas
    saldototalencordoba = int(ingresos_cordobas) - int(egresos_cordobas)
    saldototalendolares= int(ingresos_dolares)- int (egresos_dolares)
    return render_template('index.html',ingresosencordobas=ingresosencordobas, ingresosendolar=ingresosendolar, egresosencordobas=egresosencordobas, egresosendolares=egresosendolares, saldototalencordoba= saldototalencordoba, saldototalendolares= saldototalendolares)
@transacciones.route('/estadisticas')
@login_required
def estadisticas():
    categoria=db.session.execute(text("SELECT * FROM categoria")).fetchall()
    return render_template('Estadisticas/index.html', categoria=categoria)


@transacciones.route('/datos/ingresos', methods=['GET'])
def get_ingresos():
    # Obtener parámetros de la solicitud
    categoria_id = request.args.get('categoria_id')  # Opcional
    fecha_inicio = request.args.get('fecha_inicio')  # Opcional
    fecha_fin = request.args.get('fecha_fin')        # Opcional

    # Construir la consulta dinámica con un JOIN para obtener el nombre de la categoría
    query = '''
        SELECT ingresos.id, ingresos.cantidad, ingresos.fecha, 
               ingresos.usuario_id, ingresos.categoria_id, 
               categoria.nombre AS categoria_nombre
        FROM ingresos
        JOIN categoria ON ingresos.categoria_id = categoria.id
        WHERE ingresos.usuario_id = :usuario_id
    '''
    params = {'usuario_id': session['usuario_id']}

    # Agregar filtros dinámicos
    if categoria_id:
        query += ' AND ingresos.categoria_id = :categoria_id'
        params['categoria_id'] = categoria_id
    if fecha_inicio:
        query += ' AND ingresos.fecha >= :fecha_inicio'
        params['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        query += ' AND ingresos.fecha <= :fecha_fin'
        params['fecha_fin'] = fecha_fin

    # Ejecutar la consulta
    ingresos = db.session.execute(text(query), params).fetchall()

    # Convertir el resultado a una lista de diccionarios
    ingresos_list = [dict(row._mapping) for row in ingresos]

    return jsonify(ingresos_list)


@transacciones.route('/datos/ingresos_por_categoria', methods=['GET'])
def get_ingresos_por_categoria():
    # Obtener parámetros de filtro opcionales
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    # Construir la consulta dinámica
    query = '''
        SELECT categoria.nombre AS categoria_nombre, 
               SUM(ingresos.cantidad) AS total
        FROM ingresos
        JOIN categoria ON ingresos.categoria_id = categoria.id
        WHERE ingresos.usuario_id = :usuario_id
    '''
    params = {'usuario_id': session['usuario_id']}

    if fecha_inicio:
        query += ' AND ingresos.fecha >= :fecha_inicio'
        params['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        query += ' AND ingresos.fecha <= :fecha_fin'
        params['fecha_fin'] = fecha_fin

    query += ' GROUP BY categoria.id, categoria.nombre'

    # Ejecutar la consulta
    ingresos = db.session.execute(text(query), params).fetchall()

    # Convertir el resultado a una lista de diccionarios
    ingresos_list = [dict(row._mapping) for row in ingresos]

    return jsonify(ingresos_list)


@transacciones.route('/datos/ingresos_vs_egresos', methods=['GET'])
def get_ingresos_vs_egresos():
    # Obtener parámetros de la solicitud
    fecha_inicio = request.args.get('fecha_inicio')  # Opcional
    fecha_fin = request.args.get('fecha_fin')        # Opcional

    # Consulta de ingresos
    query_ingresos = 'SELECT fecha, SUM(cantidad) as total FROM ingresos WHERE usuario_id = :usuario_id'
    params = {'usuario_id': session['usuario_id']}
    if fecha_inicio:
        query_ingresos += ' AND fecha >= :fecha_inicio'
        params['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        query_ingresos += ' AND fecha <= :fecha_fin'
        params['fecha_fin'] = fecha_fin
    query_ingresos += ' GROUP BY fecha ORDER BY fecha'
    
    # Consulta de egresos
    query_egresos = 'SELECT fecha, SUM(cantidad) as total FROM egresos WHERE usuario_id = :usuario_id'
    params_egresos = {'usuario_id': session['usuario_id']}
    if fecha_inicio:
        query_egresos += ' AND fecha >= :fecha_inicio'
        params_egresos['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        query_egresos += ' AND fecha <= :fecha_fin'
        params_egresos['fecha_fin'] = fecha_fin
    query_egresos += ' GROUP BY fecha ORDER BY fecha'

    # Ejecutar las consultas
    ingresos = db.session.execute(text(query_ingresos), params).fetchall()
    egresos = db.session.execute(text(query_egresos), params_egresos).fetchall()

    # Convertir el resultado a diccionarios
    ingresos_list = [dict(row._mapping) for row in ingresos]
    egresos_list = [dict(row._mapping) for row in egresos]

    # Combinar los datos de ingresos y egresos por fecha
    fechas = list(set([row['fecha'] for row in ingresos_list + egresos_list]))
    fechas.sort()

    ingresos_por_fecha = {row['fecha']: row['total'] for row in ingresos_list}
    egresos_por_fecha = {row['fecha']: row['total'] for row in egresos_list}

    # Preparar los datos para el gráfico
    data = {
        'fechas': fechas,
        'ingresos': [ingresos_por_fecha.get(fecha, 0) for fecha in fechas],
        'egresos': [egresos_por_fecha.get(fecha, 0) for fecha in fechas],
    }

    return jsonify(data)
@transacciones.route('/datos/egresos', methods=['GET'])
def get_egresos():
    # Obtener parámetros de la solicitud
    categoria_id = request.args.get('categoria_id')  # Opcional
    fecha_inicio = request.args.get('fecha_inicio')  # Opcional
    fecha_fin = request.args.get('fecha_fin')        # Opcional

    # Construir la consulta dinámica con un JOIN para obtener el nombre de la categoría
    query = '''
        SELECT egresos.id, egresos.cantidad, egresos.fecha, 
               egresos.usuario_id, egresos.categoria_id, 
               categoria.nombre AS categoria_nombre
        FROM egresos
        JOIN categoria ON egresos.categoria_id = categoria.id
        WHERE egresos.usuario_id = :usuario_id
    '''
    params = {'usuario_id': session['usuario_id']}

    # Agregar filtros dinámicos
    if categoria_id:
        query += ' AND egresos.categoria_id = :categoria_id'
        params['categoria_id'] = categoria_id
    if fecha_inicio:
        query += ' AND egresos.fecha >= :fecha_inicio'
        params['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        query += ' AND egresos.fecha <= :fecha_fin'
        params['fecha_fin'] = fecha_fin

    # Ejecutar la consulta
    egresos = db.session.execute(text(query), params).fetchall()

    # Convertir el resultado a una lista de diccionarios
    egresos_list = [dict(row._mapping) for row in egresos]

    return jsonify(egresos_list)


@transacciones.route('/datos/egreso_por_categoria', methods=['GET'])
def get_egresos_por_categoria():
    # Obtener parámetros de filtro opcionales
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    # Construir la consulta dinámica
    query = '''
        SELECT categoria.nombre AS categoria_nombre, 
               SUM(egresos.cantidad) AS total
        FROM egresos
        JOIN categoria ON egresos.categoria_id = categoria.id
        WHERE egresos.usuario_id = :usuario_id
    '''
    params = {'usuario_id': session['usuario_id']}

    if fecha_inicio:
        query += ' AND egresos.fecha >= :fecha_inicio'
        params['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        query += ' AND egresos.fecha <= :fecha_fin'
        params['fecha_fin'] = fecha_fin

    query += ' GROUP BY categoria.id, categoria.nombre'

    # Ejecutar la consulta
    egresos = db.session.execute(text(query), params).fetchall()

    # Convertir el resultado a una lista de diccionarios
    egresos_list = [dict(row._mapping) for row in egresos]

    return jsonify(egresos_list)
