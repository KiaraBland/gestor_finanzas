from flask import Blueprint, render_template, request, redirect, url_for, flash,session,jsonify
from sqlalchemy import text
from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.helper import login_required
import cohere
import datetime
from datetime import datetime, timedelta,date

asistente = Blueprint("asistente", __name__)
co = cohere.Client('fltZXX9t7Jf0NHYlDXV146ArHyfK4KpbGNSHXNlg')



@asistente.route("/calendario", methods=["GET", "POST"])
def calendario():
    return render_template("asistente/formulario.html")

@asistente.route("/asistente", methods=["GET", "POST"])
def ia():
    return render_template("asistente/respuesta.html")

# Ruta para obtener los consejos financieros
@asistente.route("/consejos", methods=["GET", "POST"])
@login_required
def consejos():
    if request.method == "POST":
        # Obtener datos del formulario
        data = request.get_json() 
        mensaje_usuario = data.get("mensaje")
        tema = data.get("tema")
        usuario_id = session.get("usuario_id")  # Asegúrate de tener esta sesión activa

        if not mensaje_usuario or not tema:
            flash("Por favor, ingresa un mensaje y selecciona un tema.", "error")
            return redirect(url_for("asistente.consejos"))

        try:
            # Obtener datos financieros del usuario
            datos_financieros = obtener_resumen_financiero(usuario_id)

            # Generar el prompt con los datos financieros
            prompt = generar_prompt_con_datos_financieros(mensaje_usuario, tema, datos_financieros)

            # Imprimir el prompt generado para depurar
            print(f"Prompt generado:\n{prompt}")

            # Consultar a Cohere
            response = co.generate(
                model="command-xlarge-nightly",
                prompt=prompt,
              
                temperature=0.2,
                 max_tokens=400,
                  stop_sequences=["\n", "Responde", "Resumen"]
            )

            respuesta = response.generations[0].text.strip()
            
            # Imprimir la respuesta para depurar
            print(f"Respuesta generada: {respuesta}")

            # Validar relevancia de la respuesta
            if not es_relevante(respuesta,tema):
                respuesta = "No tengo informacion suficiente"

         

        except Exception as e:
            print(f"Error al generar el consejo: {e}")
            flash("Hubo un problema al generar el consejo. Inténtalo más tarde.", "error")
            respuesta = None

        # Renderizar la respuesta en la plantilla
        return jsonify({'respuesta':respuesta})

    # Renderizar el formulario en caso de GET
    return "TODO"
def obtener_resumen_financiero(usuario_id):
    sql = text("""
        SELECT 
            SUM(CASE WHEN tipo = 'Ingreso' THEN cantidad ELSE 0 END) AS total_ingresos,
            SUM(CASE WHEN tipo = 'Egreso' THEN cantidad ELSE 0 END) AS total_egresos,
            SUM(cantidad) AS saldo_actual,
            (SELECT concepto FROM movimientos WHERE tipo = 'Egreso'
             GROUP BY concepto ORDER BY SUM(cantidad) DESC LIMIT 1) AS categoria_mas_gastos
        FROM movimientos
        WHERE usuario_id = :usuario_id
    """)

    resumen = db.session.execute(sql, {"usuario_id": usuario_id}).fetchone()

    # Acceder a los resultados por índice
    if resumen:
        return {
            "total_ingresos": resumen[0] if resumen[0] else 0,  # Total ingresos
            "total_egresos": resumen[1] if resumen[1] else 0,   # Total egresos
            "saldo_actual": resumen[2] if resumen[2] else 0,    # Saldo actual
            "categoria_mas_gastos": resumen[3] if resumen[3] else "N/A"  # Categoría más gastos
        }
    else:
        return {
            "total_ingresos": 0,
            "total_egresos": 0,
            "saldo_actual": 0,
            "categoria_mas_gastos": "N/A"
        }



# Función para generar el prompt con los datos financieros
def generar_prompt_con_datos_financieros(mensaje_usuario, tema, datos_financieros):
    resumen_financiero = (
        f"Tienes un ingreso total de {datos_financieros['total_ingresos']} "
        f"y un gasto total de {datos_financieros['total_egresos']}. "
        f"Tu saldo actual es {datos_financieros['saldo_actual']}. "
        f"Tu categoría de gasto más alta es '{datos_financieros['categoria_mas_gastos']}'.\n"
    )

    prompt = f"""
    Responde de manera breve y directa sobre el tema '{tema}' basándote en la siguiente información financiera:
    {resumen_financiero}

    Pregunta: {mensaje_usuario}

    Responde en no más de 3 frases.
    """
    
    return prompt



# Función para validar la relevancia de la respuesta
def es_relevante(respuesta, tema):
    palabras_clave = {
        "Consejos financieros": ["ahorro", "presupuesto", "inversiones", "deuda", "dinero", "flujo de caja"],
        "Emprendimientos": ["negocio", "emprender", "capital", "startup", "clientes"],
        "Gestión del dinero": ["fondo de emergencia", "gastos", "ingresos", "deudas", "ahorro"]
    }

    # Convertir la respuesta a minúsculas para hacer la comparación insensible a mayúsculas/minúsculas
    respuesta_lower = respuesta.lower()

    # Verificar si la respuesta contiene palabras clave del tema
    print(f"Validando relevancia para el tema '{tema}':")
    print(f"Respuesta: {respuesta}")
    print(f"Palabras clave: {palabras_clave.get(tema)}")
    
    # Mejorar la comparación con un chequeo más flexible
    return any(palabra in respuesta_lower for palabra in palabras_clave.get(tema, []))




@asistente.route('/egresos_mes', methods=['GET'])
@login_required
def egresos_mes():
    try:
        # Obtener la fecha actual y el primer y último día del mes
        fecha_actual = datetime.now()
        primer_dia_mes = fecha_actual.replace(day=1)
        ultimo_dia_mes = fecha_actual.replace(day=28) + timedelta(days=4)  # Esto da el 1ro del siguiente mes
        ultimo_dia_mes = ultimo_dia_mes - timedelta(days=ultimo_dia_mes.day)  # Ahora es el último día del mes actual

        # Convertir las fechas a formato string adecuado
        fecha_inicio = primer_dia_mes.strftime('%Y-%m-%d')
        fecha_fin = ultimo_dia_mes.strftime('%Y-%m-%d')

        # Consultar los egresos dentro del rango de fechas y unirse con las tablas de Categoria y divisa
        egresos = db.session.execute(
            text("""
                SELECT e.id, e.cantidad, e.fecha_pago, e.habitual, e.estado, 
                       c.nombre AS categoria, d.nombre AS divisa, d.simbolo
                FROM egresos e
                JOIN Categoria c ON e.categoria_id = c.id
                JOIN divisa d ON e.divisa_id = d.id
                WHERE e.fecha_pago BETWEEN :inicio AND :fin 
                AND e.usuario_id = :usuario_id
            """),
            {"inicio": fecha_inicio, "fin": fecha_fin, "usuario_id": session['usuario_id']}
        ).fetchall()

        # Si no se encuentran egresos para el mes
        if not egresos:
            return jsonify({'message': 'No hay egresos en este mes.'}), 404

        # Convertir los resultados a un formato adecuado para la respuesta
        egresos_data = []
        for egreso in egresos:
            # Formatear la fecha correctamente (YYYY-MM-DD)
            fecha_pago = egreso[2].strftime('%Y-%m-%d') if isinstance(egreso[2], datetime) else egreso[2]
            
            egresos_data.append({
                'id': egreso[0],
                'categoria': egreso[5],  # Nombre de la categoría
                'divisa': egreso[6],     # Nombre de la divisa
                'simbolo': egreso[7],    # Símbolo de la divisa
                'cantidad': str(egreso[1]),  # Asegurarse de que la cantidad sea un string, o convertirla a número si necesario
                'fecha_pago': fecha_pago,  # Asegúrate de devolver la fecha en formato adecuado
                'habitual': egreso[3],
                'estado': egreso[4]
            })

        return jsonify(egresos_data)

    except Exception as e:
        return jsonify({'message': str(e)}), 500
@asistente.route('/egresos_por_pagar', methods=['GET'])
@login_required
def egresos_por_pagar():
    try:
        # Obtener los egresos con estado pendiente (estado = 0), y hacer JOIN con Categoria y divisa
        egresos = db.session.execute(
            text("""
                SELECT 
                    egreso.id, 
                    categoria.nombre AS categoria, 
                    divisa.nombre AS divisa, 
                    egreso.cantidad, 
                    egreso.fecha_pago, 
                    egreso.habitual, 
                    egreso.estado
                FROM 
                    egresos egreso
                JOIN 
                    Categoria categoria ON egreso.categoria_id = categoria.id
                JOIN 
                    divisa divisa ON egreso.divisa_id = divisa.id
                WHERE 
                    egreso.estado = 0 AND egreso.usuario_id = :usuario_id
            """),
            {"usuario_id": session['usuario_id']}
        ).fetchall()

        # Si no se encuentran egresos por pagar
        if not egresos:
            return jsonify({'message': 'No hay egresos pendientes por pagar.'}), 404

        # Convertir los resultados a un formato adecuado para la respuesta
        egresos_data = []
        for egreso in egresos:
            # Verifica si la fecha de pago es un objeto `datetime` o `date`
            fecha_pago = str(egreso[4])  # Convertimos la fecha a string si no es un datetime
            if isinstance(egreso[4], (datetime, date)):  # Verifica si la fecha de pago es tipo datetime o date
                fecha_pago = egreso[4].strftime('%Y-%m-%d')  # Formateamos la fecha

            # Si el estado es un datetime o date, lo formateamos
            estado = str(egreso[6])  # Deberías revisar si `estado` es un datetime, si lo es, conviértelo igual

            egresos_data.append({
                'id': egreso[0],
                'categoria': egreso[1],
                'divisa': egreso[2],
                'cantidad': egreso[3],
                'fecha_pago': fecha_pago,
                'habitual': egreso[5],
                'estado': estado
            })

        return jsonify(egresos_data)

    except Exception as e:
        return jsonify({'message': str(e)}), 500