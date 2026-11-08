"""Las alertas por correo no deben repetirse ni llegar a quien no las pidió."""
import pytest

import notifications.scheduler as S
from database.models import db, Usuario
from tests.conftest import POSICION_ISS


@pytest.fixture()
def correos(client, app_modulo, monkeypatch):
    enviados = []
    monkeypatch.setattr(S, 'enviar_alerta', lambda to, asunto, html: enviados.append(to) or True)
    monkeypatch.setattr(S, 'estado_cielo', lambda: {'condicion': 'noche', 'altura_sol': -20})
    monkeypatch.setattr(S, 'posicion_actual', lambda: dict(POSICION_ISS))
    with app_modulo.app.app_context():
        db.session.add_all([
            Usuario(email='si@mail.com', password='x', recibir_alertas=True),
            Usuario(email='no@mail.com', password='x', recibir_alertas=False),
        ])
        db.session.commit()
    return enviados


def test_alerta_iss_solo_a_suscritos_y_sin_repetir(app_modulo, correos):
    S.revisar_iss(app_modulo.app)
    S.revisar_iss(app_modulo.app)
    assert correos == ['si@mail.com']


def test_alerta_iss_no_se_envia_de_dia(app_modulo, correos, monkeypatch):
    monkeypatch.setattr(S, 'estado_cielo', lambda: {'condicion': 'día', 'altura_sol': 40})
    S.revisar_iss(app_modulo.app)
    assert correos == []


def test_alerta_iss_no_se_envia_si_esta_lejos(app_modulo, correos, monkeypatch):
    lejos = dict(POSICION_ISS, lat=40.0, lon=100.0)
    monkeypatch.setattr(S, 'posicion_actual', lambda: lejos)
    S.revisar_iss(app_modulo.app)
    assert correos == []


def test_resumen_diario_una_vez_por_dia(app_modulo, correos):
    S.enviar_resumen_diario(app_modulo.app)
    S.enviar_resumen_diario(app_modulo.app)
    assert correos == ['si@mail.com']


def test_planificador_desactivado_por_defecto(app_modulo):
    with app_modulo.app.app_context():
        assert Usuario.query.count() >= 0
    assert S.iniciar_scheduler(app_modulo.app) is None
