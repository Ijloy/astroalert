from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db     = SQLAlchemy()
bcrypt = Bcrypt()

class Usuario(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    email            = db.Column(db.String(120), unique=True, nullable=False)
    password         = db.Column(db.String(200), nullable=False)
    username         = db.Column(db.String(80), unique=True, nullable=True)
    telefono_codigo  = db.Column(db.String(10), nullable=True)
    telefono_numero  = db.Column(db.String(20), nullable=True)
    fecha_nacimiento = db.Column(db.String(20), nullable=True)
    ciudad           = db.Column(db.String(100), default='Quito')
    lat              = db.Column(db.Float, default=-0.18)
    lon              = db.Column(db.Float, default=-78.47)
    creado_en        = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id':               self.id,
            'email':            self.email,
            'username':         self.username,
            'telefono':         f"{self.telefono_codigo}{self.telefono_numero}" if self.telefono_numero else None,
            'fecha_nacimiento': self.fecha_nacimiento,
            'ciudad':           self.ciudad,
            'lat':              self.lat,
            'lon':              self.lon,
        }