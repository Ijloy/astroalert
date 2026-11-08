"""Configuración común de los tests.

* Base de datos SQLite en memoria (no toca ningún archivo).
* Planificador de alertas desactivado.
* Las APIs externas (ISS, NASA) se simulan: los tests no dependen de internet.
"""
import os
import sys
from datetime import datetime, timezone

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['ENABLE_SCHEDULER'] = 'false'
os.environ['APP_ENV'] = 'development'
os.environ['RATELIMIT_STORAGE_URI'] = 'memory://'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

POSICION_ISS = {'lat': -1.0, 'lon': -79.0, 'altitud': 418.0, 'velocidad': 27600.0,
                'timestamp': datetime(2026, 11, 8, tzinfo=timezone.utc)}


@pytest.fixture(scope='session')
def app_modulo():
    import app as modulo
    modulo.app.config['TESTING'] = True
    return modulo


@pytest.fixture()
def client(app_modulo, monkeypatch):
    from database.models import db
    from extensions import limiter
    monkeypatch.setattr(app_modulo, 'posicion_actual', lambda: dict(POSICION_ISS))
    monkeypatch.setattr(app_modulo, 'imagen_del_dia',
                        lambda: {'titulo': 'Nebulosa', 'url': 'https://example.com/a.jpg', 'pagina': 'https://apod.nasa.gov'})
    limiter.reset()
    with app_modulo.app.app_context():
        db.drop_all()
        db.create_all()
    return app_modulo.app.test_client()


@pytest.fixture()
def registrar(client):
    def _registrar(email='dereck@mail.com', password='clave-segura', **extra):
        datos = {'email': email, 'password': password, 'confirmar_password': password, **extra}
        return client.post('/api/registro', json=datos)
    return _registrar


@pytest.fixture()
def token(client, registrar):
    registrar(recibir_alertas=True)
    r = client.post('/api/login', json={'email': 'dereck@mail.com', 'password': 'clave-segura'})
    return r.get_json()['token']
