from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database.models import db, Usuario
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@auth_bp.route('/api/registro', methods=['POST'])
def registro():
    datos = request.get_json()
    if not datos or not datos.get('email') or not datos.get('password'):
        return jsonify({'error': 'Email y password requeridos'}), 400

    if datos.get('password') != datos.get('confirmar_password'):
        return jsonify({'error': 'Las contraseñas no coinciden'}), 400

    if Usuario.query.filter_by(email=datos['email']).first():
        return jsonify({'error': 'Email ya registrado'}), 409

    if datos.get('username') and Usuario.query.filter_by(username=datos['username']).first():
        return jsonify({'error': 'Nombre de usuario ya en uso'}), 409

    if datos.get('fecha_nacimiento') and not validar_fecha(datos['fecha_nacimiento']):
        return jsonify({'error': 'Fecha de nacimiento inválida'}), 400

    usuario = Usuario(
        email            = datos['email'],
        username         = datos.get('username'),
        telefono_codigo  = datos.get('telefono_codigo', '+593'),
        telefono_numero  = datos.get('telefono_numero'),
        fecha_nacimiento = datos.get('fecha_nacimiento'),
    )
    usuario.set_password(datos['password'])
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario creado', 'usuario': usuario.to_dict()}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    datos   = request.get_json()
    usuario = Usuario.query.filter_by(email=datos.get('email')).first()
    if not usuario or not usuario.check_password(datos.get('password', '')):
        return jsonify({'error': 'Credenciales incorrectas'}), 401
    token = create_access_token(identity=str(usuario.id))
    return jsonify({'token': token, 'usuario': usuario.to_dict()})

@auth_bp.route('/api/perfil', methods=['GET'])
@jwt_required()
def perfil():
    usuario = Usuario.query.get(int(get_jwt_identity()))
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario.to_dict())