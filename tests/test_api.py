"""Rutas web y endpoints públicos de la API."""
import pytest


@pytest.mark.parametrize('ruta', ['/', '/eclipses', '/iss', '/lunas', '/telescopio', '/proximamente'])
def test_paginas_web(client, ruta):
    r = client.get(ruta)
    assert r.status_code == 200
    assert b'AstroAlert' in r.data


def test_ruta_desconocida_404(client):
    assert client.get('/no-existe').status_code == 404


def test_ruta_antigua_web_redirige(client):
    r = client.get('/web')
    assert r.status_code == 301 and r.headers['Location'].endswith('/')


def test_health(client):
    assert client.get('/api/health').get_json() == {'status': 'ok', 'db': 'ok'}


def test_errores_de_api_en_json(client):
    r = client.get('/api/no-existe')
    assert r.status_code == 404
    assert r.get_json() == {'error': 'Recurso no encontrado'}


def test_cabeceras_de_seguridad(client):
    h = client.get('/').headers
    assert h['X-Content-Type-Options'] == 'nosniff'
    assert h['X-Frame-Options'] == 'DENY'


def test_iss(client):
    data = client.get('/api/iss').get_json()
    assert data['posicion']['altitud'] == 418.0
    assert data['distancia_desde_ciudad'] > 0


def test_iss_caida_devuelve_503(client, app_modulo, monkeypatch):
    import requests

    def falla():
        raise requests.ConnectionError('sin red')
    monkeypatch.setattr(app_modulo, 'posicion_actual', falla)
    r = client.get('/api/iss')
    assert r.status_code == 503 and 'error' in r.get_json()


@pytest.mark.parametrize('ruta, clave', [
    ('/api/eclipses', 'eclipses'), ('/api/conjunciones', 'conjunciones'),
    ('/api/oposiciones', 'oposiciones'), ('/api/cometas', 'cometas'), ('/api/lunas', 'lunas'),
])
def test_listas_de_eventos(client, ruta, clave):
    r = client.get(ruta)
    assert r.status_code == 200
    assert isinstance(r.get_json()[clave], list)


def test_planetas_incluye_estado_del_cielo(client):
    data = client.get('/api/planetas').get_json()
    assert data['cielo']['condicion'] in ('día', 'crepúsculo', 'noche')


def test_luna_inexistente(client):
    assert client.get('/api/lunas/pluton-b').status_code == 404


def test_cometas_con_fuente(client):
    for c in client.get('/api/cometas').get_json()['cometas']:
        assert c['fuente'].startswith('https://')


@pytest.mark.parametrize('cuerpo, mensaje', [
    ({}, 'La apertura'),
    ({'apertura_mm': 130, 'focal_telescopio_mm': 1000, 'focal_ocular_mm': 0}, 'La focal del ocular'),
    ({'apertura_mm': 'abc', 'focal_telescopio_mm': 1000, 'focal_ocular_mm': 10}, 'La apertura'),
])
def test_telescopio_valida_datos(client, cuerpo, mensaje):
    r = client.post('/api/telescopio', json=cuerpo)
    assert r.status_code == 400
    assert mensaje in r.get_json()['error']


def test_telescopio_ok(client):
    r = client.post('/api/telescopio', json={'apertura_mm': 130, 'focal_telescopio_mm': 1000, 'focal_ocular_mm': 10})
    assert r.status_code == 200
    assert r.get_json()['resultados']['magnificacion'] == 100
