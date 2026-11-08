from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db     = SQLAlchemy()
bcrypt = Bcrypt()


def _ahora():
    return datetime.now(timezone.utc)


class Usuario(db.Model):
    """Cuenta de usuario. Solo se guarda lo necesario para enviar alertas.

    Se eliminaron teléfono y fecha de nacimiento: no se usaban y guardar datos
    personales innecesarios es un riesgo (minimización de datos).
    """
    id        = db.Column(db.Integer, primary_key=True)
    email     = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password  = db.Column(db.String(200), nullable=False)
    username  = db.Column(db.String(30), unique=True, nullable=True)
    ciudad    = db.Column(db.String(100), default='Quito')
    lat       = db.Column(db.Float, default=-0.18)
    lon       = db.Column(db.Float, default=-78.47)
    creado_en = db.Column(db.DateTime(timezone=True), default=_ahora)

    # Alertas: desactivadas por defecto (el usuario decide)
    recibir_alertas       = db.Column(db.Boolean, default=False, nullable=False)
    ultima_alerta_iss     = db.Column(db.DateTime(timezone=True), nullable=True)
    ultimo_resumen_diario = db.Column(db.Date, nullable=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id':              self.id,
            'email':           self.email,
            'username':        self.username,
            'ciudad':          self.ciudad,
            'recibir_alertas': self.recibir_alertas,
        }
