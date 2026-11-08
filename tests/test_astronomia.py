"""Cálculos astronómicos comparados con datos de referencia publicados."""
from datetime import datetime, timezone, timedelta

import pytest
from skyfield.api import wgs84

from events.efemerides import TS, TIERRA, cuenta_regresiva
from events import eclipses, oposiciones, sky, conjunciones
from events.telescopio import calcular_telescopio


def utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


# ───────────── Eclipses solares ─────────────
@pytest.fixture(scope='module')
def solares_2027_2029():
    t0, t1 = TS.from_datetime(utc(2027, 1, 1)), TS.from_datetime(utc(2029, 2, 1))
    return {e['fecha_utc'].date().isoformat(): e for e in eclipses._eclipses_solares(t0, t1)}


@pytest.mark.parametrize('fecha, tipo', [
    ('2027-02-06', 'Anular'),
    ('2027-08-02', 'Total'),
    ('2028-01-26', 'Anular'),
    ('2028-07-22', 'Total'),
    ('2029-01-14', 'Parcial'),
])
def test_tipo_global_de_eclipses_solares_coincide_con_nasa(solares_2027_2029, fecha, tipo):
    assert fecha in solares_2027_2029, f'No se detectó el eclipse del {fecha}'
    assert solares_2027_2029[fecha]['subtipo'] == tipo


def test_no_se_inventan_eclipses_solares(solares_2027_2029):
    assert len(solares_2027_2029) == 5


def test_eclipse_total_2027_no_se_ve_desde_quito(solares_2027_2029):
    assert solares_2027_2029['2027-08-02']['visible_local'] is False


def test_eclipse_anular_2028_se_ve_parcial_desde_quito(solares_2027_2029):
    local = solares_2027_2029['2028-01-26']['local']
    assert local['tipo'] == 'Parcial'
    assert 0.8 < local['magnitud'] < 0.9


def test_eclipse_anular_2028_en_salinas():
    """Referencia (solar-eclipse.info): anular en Salinas, magnitud 0.917, ~2 min 47 s."""
    salinas = TIERRA + wgs84.latlon(-2.2149, -80.9524, elevation_m=10)
    t0, t1 = TS.from_datetime(utc(2028, 1, 20)), TS.from_datetime(utc(2028, 2, 1))
    (evento,) = eclipses._eclipses_solares(t0, t1, salinas)
    local = evento['local']
    assert local['tipo'] == 'Anular'
    assert local['magnitud'] == pytest.approx(0.917, abs=0.005)
    assert 120 <= local['duracion_central_s'] <= 200


def test_eclipses_lunares_solo_visibles_con_la_luna_arriba():
    t0, t1 = TS.from_datetime(utc(2027, 1, 1)), TS.from_datetime(utc(2029, 1, 1))
    for e in eclipses._eclipses_lunares(t0, t1):
        assert e['visible_local'] == (e['local']['altura_luna'] > 0)


# ───────────── Planetas ─────────────
def test_de_dia_no_hay_planetas_visibles():
    mediodia_quito = TS.from_datetime(utc(2026, 11, 8, 17, 0))   # 12:00 en Quito
    assert sky.estado_cielo(mediodia_quito)['condicion'] == 'día'
    assert sky.planetas_visibles(mediodia_quito) == []


def test_proxima_ventana_es_de_noche():
    desde = TS.from_datetime(utc(2026, 11, 8, 17, 0))
    ventana = sky.proxima_ventana(desde=desde)
    assert ventana is not None
    t = TS.from_datetime(utc(2026, 11, 8, 17, 0) + timedelta(minutes=ventana['en_minutos']))
    assert sky.altura_sol(t) <= sky.SOL_MAX


# ───────────── Oposiciones ─────────────
@pytest.mark.parametrize('planeta, fecha', [
    ('Urano',   '2026-11-25'),
    ('Júpiter', '2027-02-10'),
    ('Marte',   '2027-02-19'),
])
def test_fechas_de_oposicion(planeta, fecha):
    eventos = {e['planeta']: e for e in oposiciones.calcular_oposiciones(utc(2026, 11, 1))}
    # La hora puede caer en el día siguiente en UTC: se acepta ±1 día
    real = eventos[planeta]['fecha_utc'].date()
    esperado = datetime.fromisoformat(fecha).date()
    assert abs((real - esperado).days) <= 1
    assert eventos[planeta]['elongacion'] > 175


# ───────────── Conjunciones ─────────────
def test_conjunciones_ordenadas_y_cercanas():
    lista = conjunciones.proximas_conjunciones()
    assert lista == sorted(lista, key=lambda c: c['timestamp'])
    assert all(c['separacion'] <= conjunciones.SEPARACION_MAX for c in lista)


# ───────────── Telescopio y utilidades ─────────────
def test_calculadora_de_telescopio():
    r = calcular_telescopio(130, 1000, 10)['resultados']
    assert r['magnificacion'] == 100
    assert r['relacion_focal'] == 'f/7.7'
    assert r['pupila_salida'] == 1.3
    assert r['mag_maxima_util'] == 260


def test_telescopio_avisa_aumento_excesivo():
    assert calcular_telescopio(60, 1200, 4)['advertencias']


def test_cuenta_regresiva_nunca_negativa():
    assert cuenta_regresiva(datetime.now(timezone.utc) - timedelta(days=3))['dias'] == 0
