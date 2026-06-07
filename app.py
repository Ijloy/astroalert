from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database.models import db, bcrypt
from routes.auth import auth_bp
from events.iss import posicion_actual, distancia_km
from events.sky import planetas_visibles, proxima_ventana
from config import LAT, LON, CITY, SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL
from flask import Flask, jsonify, render_template
from notifications.scheduler import iniciar_scheduler
from events.eclipses import proximos_eclipses
from events.conjunciones import proximas_conjunciones



app = Flask(__name__)
@app.route('/web')
def web():
    return render_template('index.html')
CORS(app)

app.config['SECRET_KEY']                  = SECRET_KEY
app.config['JWT_SECRET_KEY']              = JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI']     = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
JWTManager(app)
app.register_blueprint(auth_bp) 

with app.app_context():
    db.create_all()

@app.route('/')
def inicio():
    return jsonify({'app': 'AstroAlert', 'ciudad': CITY,
                    'endpoints': ['/api/iss', '/api/planetas', '/api/eventos',
                                  '/api/registro', '/api/login', '/api/perfil']})

@app.route('/api/iss')
def api_iss():
    pos = posicion_actual()
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
    return jsonify({
        'ciudad':   CITY,
        'eclipses': proximos_eclipses()
    })

@app.route('/api/eventos')
def api_eventos():
    pos = posicion_actual()
    dist = distancia_km(LAT, LON, pos['lat'], pos['lon'])
    ahora = planetas_visibles()
    ventana = proxima_ventana() if not ahora else None
    return jsonify({'ciudad': CITY,
                    'iss': {'posicion': pos, 'distancia_km': dist},
                    'planetas': {'visibles_ahora': ahora, 'proxima_ventana': ventana}})

@app.route('/api/conjunciones')
def api_conjunciones():
    return jsonify({
        'ciudad': CITY,
        'conjunciones': proximas_conjunciones()
    })


iniciar_scheduler(app)
if __name__ == '__main__':
    app.run(debug=True)