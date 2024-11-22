from flask import Blueprint, render_template, request, redirect, url_for, flash,session,jsonify
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required

transacciones = Blueprint("transacciones", __name__)


@transacciones.route('/inicio')
@login_required
def index():
    # Consultas a la base de datos para obtener los ingresos y egresos en Córdobas y Dólares
    ingresosencordobas = db.session.execute(
        text("SELECT sum(cantidad) as cantidad FROM ingresos WHERE divisa_id = 1 AND usuario_id = :usuario_id"),
        {"usuario_id": session['usuario_id']}
    ).fetchone() or (0,)

    ingresosendolar = db.session.execute(
        text("SELECT sum(cantidad) as cantidad FROM ingresos WHERE divisa_id = 2 AND usuario_id = :usuario_id"),
        {"usuario_id": session['usuario_id']}
    ).fetchone() or (0,)

    egresosencordobas = db.session.execute(
        text("SELECT sum(cantidad) as cantidad FROM egresos WHERE divisa_id = 1 AND usuario_id = :usuario_id"),
        {"usuario_id": session['usuario_id']}
    ).fetchone() or (0,)

    egresosendolares = db.session.execute(
        text("SELECT sum(cantidad) as cantidad FROM egresos WHERE divisa_id = 2 AND usuario_id = :usuario_id"),
        {"usuario_id": session['usuario_id']}
    ).fetchone() or (0,)

    # Obtener los valores de las consultas o asignar 0 si es None
    ingresos_cordobas = ingresosencordobas[0] if ingresosencordobas[0] is not None else 0
    ingresos_dolares = ingresosendolar[0] if ingresosendolar[0] is not None else 0
    egresos_cordobas = egresosencordobas[0] if egresosencordobas[0] is not None else 0
    egresos_dolares = egresosendolares[0] if egresosendolares[0] is not None else 0

    # Consultar transacciones recientes
    transacciones = db.session.execute(
        text("SELECT * FROM movimientos WHERE usuario_id = :usuario_id ORDER BY fecha DESC LIMIT 3"),
        {"usuario_id": session['usuario_id']}
    ).fetchall()

    ingresos_cordobas = ingresosencordobas[0] or 0
    egresos_cordobas = egresosencordobas[0] or 0
    ingresos_dolares = ingresosendolar[0] or 0
    egresos_dolares = egresosendolares[0] or 0
    print(ingresos_cordobas)
    print(egresos_cordobas)
    print(egresos_dolares)
    print(ingresos_dolares)

    # Asegúrate de que no sean None antes de la comparación
    saldototalencordoba = ingresos_cordobas - egresos_cordobas if ingresos_cordobas is not None and egresos_cordobas is not None else 0
    saldototalendolares = ingresos_dolares - egresos_dolares if ingresos_dolares is not None and egresos_dolares is not None else 0


    # Pasar los datos a la plantilla
    return render_template(
        'index.html',
        ingresosencordobas=ingresos_cordobas,
        ingresosendolar=ingresos_dolares,
        egresosencordobas=egresos_cordobas,
        egresosendolares=egresos_dolares,
        saldototalencordoba=saldototalencordoba,
        saldototalendolares=saldototalendolares,
        transacciones=transacciones
    )


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
