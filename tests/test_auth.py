"""Registro, login, límite de intentos y preferencias de alertas."""
import pytest


@pytest.mark.parametrize('datos, error', [
    ({'email': 'a', 'password': 'clave-segura'}, 'El email no es válido'),
    ({'email': 'a@b.com', 'password': '1234'}, 'al menos 8 caracteres'),
    ({'email': '', 'password': ''}, 'requeridos'),
])
def test_registro_valida(registrar, datos, error):
    r = registrar(**datos)
    assert r.status_code == 400
    assert error in r.get_json()['error']


def test_registro_contrasenas_distintas(client):
    r = client.post('/api/registro', json={'email': 'a@b.com', 'password': 'clave-segura', 'confirmar_password': 'otra-clave'})
    assert r.status_code == 400


def test_registro_ok_y_email_en_minusculas(registrar):
    r = registrar(email='Dereck@Mail.COM')
    assert r.status_code == 201
    assert r.get_json()['usuario']['email'] == 'dereck@mail.com'
    assert r.get_json()['usuario']['recibir_alertas'] is False   # alertas apagadas por defecto


def test_registro_duplicado_aunque_cambien_mayusculas(registrar):
    registrar(email='dereck@mail.com')
    assert registrar(email='DERECK@mail.com').status_code == 409


def test_login_incorrecto_no_revela_si_existe_la_cuenta(client, registrar):
    registrar()
    r1 = client.post('/api/login', json={'email': 'dereck@mail.com', 'password': 'mala-clave'})
    r2 = client.post('/api/login', json={'email': 'nadie@mail.com', 'password': 'mala-clave'})
    assert r1.status_code == r2.status_code == 401
    assert r1.get_json() == r2.get_json()


def test_login_sin_json_no_rompe(client):
    assert client.post('/api/login', data='hola', content_type='text/plain').status_code == 401


def test_limite_de_intentos_de_login(client):
    codigos = [client.post('/api/login', json={'email': 'x@y.com', 'password': 'mal'}).status_code for _ in range(12)]
    assert codigos[:10] == [401] * 10
    assert codigos[-1] == 429


def test_perfil_requiere_token(client):
    assert client.get('/api/perfil').status_code == 401


def test_perfil_y_alertas(client, token):
    h = {'Authorization': f'Bearer {token}'}
    assert client.get('/api/perfil', headers=h).get_json()['recibir_alertas'] is True
    r = client.patch('/api/perfil/alertas', json={'recibir_alertas': False}, headers=h)
    assert r.status_code == 200 and r.get_json()['recibir_alertas'] is False
    assert client.patch('/api/perfil/alertas', json={'recibir_alertas': 'si'}, headers=h).status_code == 400
