"""Registro, login y perfil.

La cuenta es opcional: solo sirve para recibir alertas por correo.
"""
import re
from datetime import timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from database.models import db, Usuario
from extensions import limiter

auth_bp = Blueprint('auth', __name__)

EMAIL_RE    = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
PASSWORD_MIN = 8
TOKEN_DURACION = timedelta(days=7)


def _datos():
    """JSON del cuerpo o {} si no es JSON válido (antes el login fallaba con 500/415)."""
    return request.get_json(silent=True) or {}


def validar_registro(datos):
    """Devuelve un mensaje de error o None si los datos son válidos."""
    email    = (datos.get('email') or '').strip().lower()
    password = datos.get('password') or ''
    username = (datos.get('username') or '').strip()

    if not email or not password:
        return 'Email y contraseña son requeridos'
    if len(email) > 254 or not EMAIL_RE.match(email):
        return 'El email no es válido'
    if len(password) < PASSWORD_MIN:
        return f'La contraseña debe tener al menos {PASSWORD_MIN} caracteres'
    if len(password) > 128:
        return 'La contraseña es demasiado larga'
    if password != datos.get('confirmar_password'):
        return 'Las contraseñas no coinciden'
    if username and not USERNAME_RE.match(username):
        return 'El usuario debe tener 3-30 caracteres: letras, números, punto, guion o guion bajo'
    return None


@auth_bp.route('/api/registro', methods=['POST'])
@limiter.limit("5 per minute; 30 per hour")
def registro():
    datos = _datos()
    error = validar_registro(datos)
    if error:
        return jsonify({'error': error}), 400

    email    = datos['email'].strip().lower()
    username = (datos.get('username') or '').strip() or None

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'error': 'Ese email ya está registrado'}), 409
    if username and Usuario.query.filter_by(username=username).first():
        return jsonify({'error': 'Ese nombre de usuario ya está en uso'}), 409

    usuario = Usuario(email=email, username=username,
                      recibir_alertas=bool(datos.get('recibir_alertas', False)))
    usuario.set_password(datos['password'])
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario creado', 'usuario': usuario.to_dict()}), 201


@auth_bp.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute; 100 per hour")
def login():
    datos   = _datos()
    email   = (datos.get('email') or '').strip().lower()
    usuario = Usuario.query.filter_by(email=email).first() if email else None
    # Mismo mensaje si el email no existe o la contraseña está mal (no revela qué cuentas existen)
    if not usuario or not usuario.check_password(datos.get('password') or ''):
        return jsonify({'error': 'Email o contraseña incorrectos'}), 401
    token = create_access_token(identity=str(usuario.id), expires_delta=TOKEN_DURACION)
    return jsonify({'token': token, 'usuario': usuario.to_dict()})


def _usuario_actual():
    return db.session.get(Usuario, int(get_jwt_identity()))


@auth_bp.route('/api/perfil', methods=['GET'])
@jwt_required()
def perfil():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario.to_dict())


@auth_bp.route('/api/perfil/alertas', methods=['PATCH'])
@jwt_required()
def preferencias_alertas():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    valor = _datos().get('recibir_alertas')
    if not isinstance(valor, bool):
        return jsonify({'error': 'recibir_alertas debe ser true o false'}), 400
    usuario.recibir_alertas = valor
    db.session.commit()
    return jsonify(usuario.to_dict())
