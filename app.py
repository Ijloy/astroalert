from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database.models import db, bcrypt
from routes.auth import auth_bp
from events.iss import posicion_actual, distancia_km
from events.sky import planetas_visibles, proxima_ventana
from events.eclipses import proximos_eclipses
from events.conjunciones import proximas_conjunciones
from events.lunas import obtener_lunas, obtener_luna, obtener_imagen_nasa
from events.cometas import obtener_cometas
from events.oposiciones import proximas_oposiciones
from events.telescopio import calcular_telescopio
from notifications.scheduler import iniciar_scheduler
from config import LAT, LON, CITY, SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY']                     = SECRET_KEY
app.config['JWT_SECRET_KEY']                 = JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI']        = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
JWTManager(app)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

@app.route('/web')
def web():
    return render_template('index.html')

@app.route('/')
def inicio():
    return jsonify({'app': 'AstroAlert', 'ciudad': CITY,
                    'endpoints': ['/api/iss', '/api/planetas', '/api/eventos',
                                  '/api/registro', '/api/login', '/api/perfil']})

@app.route('/api/iss')
def api_iss():
    pos  = posicion_actual()
    dist = distancia_km(LAT, LON, pos['lat'], pos['lon'])
    return jsonify({'posicion': pos, 'distancia_desde_ciudad': dist, 'ciudad': CITY})

@app.route('/api/planetas')
def api_planetas():
    ahora = planetas_visibles()
    if ahora:
        return jsonify({'visibles_ahora': True, 'planetas': ahora, 'ciudad': CITY})
    ventana = proxima_ventana()
    return jsonify({'visibles_ahora': False, 'proxima_ventana': ventana, 'ciudad': CITY})

@app.route('/api/eclipses')
def api_eclipses():
    return jsonify({'ciudad': CITY, 'eclipses': proximos_eclipses()})

@app.route('/api/eventos')
def api_eventos():
    pos     = posicion_actual()
    dist    = distancia_km(LAT, LON, pos['lat'], pos['lon'])
    ahora   = planetas_visibles()
    ventana = proxima_ventana() if not ahora else None
    return jsonify({'ciudad': CITY,
                    'iss':      {'posicion': pos, 'distancia_km': dist},
                    'planetas': {'visibles_ahora': ahora, 'proxima_ventana': ventana}})

@app.route('/api/conjunciones')
def api_conjunciones():
    return jsonify({'ciudad': CITY, 'conjunciones': proximas_conjunciones()})

@app.route('/api/lunas')
def api_lunas():
    return jsonify({'lunas': obtener_lunas()})

@app.route('/api/lunas/<luna_id>')
def api_luna(luna_id):
    luna = obtener_luna(luna_id)
    if not luna:
        return jsonify({'error': 'Luna no encontrada'}), 404
    return jsonify(luna)

@app.route('/api/lunas/<luna_id>/imagen')
def api_luna_imagen(luna_id):
    img = obtener_imagen_nasa(luna_id)
    if not img:
        return jsonify({'error': 'Imagen no encontrada'}), 404
    return jsonify({'imagen': img})

@app.route('/api/oposiciones')
def api_oposiciones():
    return jsonify({'ciudad': CITY, 'oposiciones': proximas_oposiciones()})

@app.route('/api/cometas')
def api_cometas():
    return jsonify({'ciudad': CITY, 'cometas': obtener_cometas()})

@app.route('/api/telescopio', methods=['POST'])
def api_telescopio():
    datos = request.get_json()
    if not datos:
        return jsonify({'error': 'Datos requeridos'}), 400

    apertura  = datos.get('apertura_mm')
    focal_tel = datos.get('focal_telescopio_mm')
    focal_oc  = datos.get('focal_ocular_mm')
    afov      = datos.get('afov', 52)

    if not all([apertura, focal_tel, focal_oc]):
        return jsonify({'error': 'apertura_mm, focal_telescopio_mm y focal_ocular_mm son requeridos'}), 400

    try:
        resultado = calcular_telescopio(
            float(apertura),
            float(focal_tel),
            float(focal_oc),
            float(afov)
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

iniciar_scheduler(app)

if __name__ == '__main__':
    app.run(debug=True)