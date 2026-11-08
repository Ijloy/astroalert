"""AstroAlert — servidor Flask: sirve la web y la API de eventos astronómicos."""
import logging
import os

import requests
from flask import Flask, jsonify, render_template, request, redirect, abort
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from config import (CITY, SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL, CORS_ORIGINS, EN_PRODUCCION, LAT, LON)
from database.models import db, bcrypt
from extensions import limiter
from routes.auth import auth_bp
from events.iss import posicion_actual, distancia_km
from events.sky import planetas_visibles, proxima_ventana, estado_cielo
from events.eclipses import proximos_eclipses
from events.conjunciones import proximas_conjunciones
from events.lunas import obtener_lunas, obtener_luna
from events.cometas import obtener_cometas
from events.oposiciones import proximas_oposiciones
from events.telescopio import calcular_telescopio
from events.apod import imagen_del_dia
from notifications.scheduler import iniciar_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("astroalert")

app = Flask(__name__)
# Render pone la app detrás de un proxy: así request.remote_addr es la IP real (para el rate limit)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

app.config.update(
    SECRET_KEY=SECRET_KEY,
    JWT_SECRET_KEY=JWT_SECRET_KEY,
    SQLALCHEMY_DATABASE_URI=DATABASE_URL,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True},
)

if CORS_ORIGINS:
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

db.init_app(app)
bcrypt.init_app(app)
limiter.init_app(app)
JWTManager(app)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()


# ══════════════════ Seguridad y errores ══════════════════
@app.after_request
def cabeceras_seguridad(resp):
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    resp.headers.setdefault('X-Frame-Options', 'DENY')
    resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    if EN_PRODUCCION:
        resp.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    return resp


@app.errorhandler(HTTPException)
def error_http(e):
    if request.path.startswith('/api'):
        mensajes = {404: 'Recurso no encontrado', 405: 'Método no permitido',
                    429: 'Demasiados intentos. Espera un momento y vuelve a intentarlo.'}
        return jsonify({'error': mensajes.get(e.code, e.description)}), e.code
    return e


@app.errorhandler(Exception)
def error_inesperado(e):
    log.exception("Error no controlado en %s", request.path)
    return jsonify({'error': 'Error interno. Inténtalo de nuevo en unos minutos.'}), 500


def servicio_externo_caido(nombre):
    return jsonify({'error': f'No pudimos consultar {nombre} ahora mismo. Inténtalo en unos minutos.'}), 503


# ══════════════════ Web ══════════════════
@app.route('/')
def inicio():
    return render_template('index.html')


SECCIONES_WEB = {'iss', 'planetas', 'eclipses', 'conjunciones', 'oposiciones',
                 'cometas', 'lunas', 'telescopio', 'proximamente'}


@app.route('/<seccion>')
def seccion_web(seccion):
    # Cada sección tiene su URL (/eclipses, /iss...): el frontend decide qué mostrar.
    if seccion not in SECCIONES_WEB:
        abort(404)
    return render_template('index.html')


@app.route('/web')
def web():
    # Ruta antigua: se mantiene para no romper enlaces ya compartidos.
    return redirect('/', code=301)


# ══════════════════ API ══════════════════
@app.route('/api')
def api_indice():
    return jsonify({'app': 'AstroAlert', 'ciudad': CITY,
                    'endpoints': ['/api/health', '/api/iss', '/api/planetas', '/api/eclipses', '/api/conjunciones',
                                  '/api/oposiciones', '/api/cometas', '/api/lunas', '/api/imagen-dia',
                                  '/api/telescopio', '/api/registro', '/api/login', '/api/perfil']})


@app.route('/api/health')
def api_health():
    try:
        db.session.execute(text('SELECT 1'))
        estado_db = 'ok'
    except Exception:
        log.exception("Health check: base de datos no disponible")
        estado_db = 'error'
    codigo = 200 if estado_db == 'ok' else 503
    return jsonify({'status': 'ok' if codigo == 200 else 'degradado', 'db': estado_db}), codigo


@app.route('/api/iss')
def api_iss():
    try:
        pos = posicion_actual()
    except requests.RequestException:
        log.warning("API de la ISS no disponible")
        return servicio_externo_caido('la posición de la ISS')
    dist = distancia_km(LAT, LON, pos['lat'], pos['lon'])
    return jsonify({'posicion': pos, 'distancia_desde_ciudad': dist, 'ciudad': CITY})


@app.route('/api/planetas')
def api_planetas():
    cielo = estado_cielo()
    ahora = planetas_visibles()
    if ahora:
        return jsonify({'visibles_ahora': True, 'planetas': ahora, 'cielo': cielo, 'ciudad': CITY})
    return jsonify({'visibles_ahora': False, 'proxima_ventana': proxima_ventana(), 'cielo': cielo, 'ciudad': CITY})


@app.route('/api/eclipses')
def api_eclipses():
    return jsonify({'ciudad': CITY, 'eclipses': proximos_eclipses()})


@app.route('/api/conjunciones')
def api_conjunciones():
    return jsonify({'ciudad': CITY, 'conjunciones': proximas_conjunciones()})


@app.route('/api/oposiciones')
def api_oposiciones():
    return jsonify({'ciudad': CITY, 'oposiciones': proximas_oposiciones()})


@app.route('/api/cometas')
def api_cometas():
    return jsonify({'ciudad': CITY, 'cometas': obtener_cometas()})


@app.route('/api/lunas')
def api_lunas():
    return jsonify({'lunas': obtener_lunas()})


@app.route('/api/lunas/<luna_id>')
def api_luna(luna_id):
    luna = obtener_luna(luna_id)
    if not luna:
        return jsonify({'error': 'Luna no encontrada'}), 404
    return jsonify(luna)


@app.route('/api/imagen-dia')
def api_imagen_dia():
    img = imagen_del_dia()
    if not img:
        return servicio_externo_caido('la imagen del día de la NASA')
    return jsonify(img)


@app.route('/api/telescopio', methods=['POST'])
def api_telescopio():
    datos = request.get_json(silent=True) or {}
    campos = {'apertura_mm': (1, 10000), 'focal_telescopio_mm': (1, 50000),
              'focal_ocular_mm': (1, 200), 'afov': (10, 120)}
    nombres = {'apertura_mm': 'La apertura', 'focal_telescopio_mm': 'La focal del telescopio',
               'focal_ocular_mm': 'La focal del ocular', 'afov': 'El campo aparente'}
    valores = {}
    for campo, (minimo, maximo) in campos.items():
        bruto = datos.get(campo, 52 if campo == 'afov' else None)
        try:
            valor = float(bruto)
        except (TypeError, ValueError):
            return jsonify({'error': f'{nombres[campo]} es requerida y debe ser un número'}), 400
        if not minimo <= valor <= maximo:
            return jsonify({'error': f'{nombres[campo]} debe estar entre {minimo} y {maximo}'}), 400
        valores[campo] = valor

    return jsonify(calcular_telescopio(valores['apertura_mm'], valores['focal_telescopio_mm'],
                                       valores['focal_ocular_mm'], valores['afov']))


iniciar_scheduler(app)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG') == '1')
