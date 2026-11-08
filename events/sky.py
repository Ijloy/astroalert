"""Planetas visibles a simple vista desde la ciudad configurada.

Un planeta se considera visible solo si:
  1. está al menos ALTURA_MIN_PLANETA grados sobre el horizonte, y
  2. el Sol está por debajo de SOL_MAX (fin del crepúsculo civil, −6°).
Antes no se revisaba el Sol, así que a mediodía la app decía que Mercurio
"se veía" a 70° de altura.
"""

import numpy as np
from skyfield.magnitudelib import planetary_magnitude

from events.efemerides import TS, TIERRA, SOL, OBSERVADOR, PLANETAS, CITY, direccion, a_local

ALTURA_MIN_PLANETA = 5.0    # grados
SOL_MAX            = -6.0   # grados (crepúsculo civil)
PASO_MINUTOS       = 15


def altura_sol(t):
    alt, _, _ = OBSERVADOR.at(t).observe(SOL).apparent().altaz()
    return alt.degrees


def condicion_cielo(alt_sol):
    if alt_sol > -0.833:
        return 'día'
    if alt_sol > SOL_MAX:
        return 'crepúsculo'
    return 'noche'


def _posiciones(t):
    """Altura, azimut y magnitud de cada planeta en el instante t."""
    resultado = []
    for nombre, cuerpo in PLANETAS.items():
        alt, az, _ = OBSERVADOR.at(t).observe(cuerpo).apparent().altaz()
        if alt.degrees < ALTURA_MIN_PLANETA:
            continue
        try:
            mag = round(float(planetary_magnitude(TIERRA.at(t).observe(cuerpo))), 1)
        except Exception:
            mag = None
        resultado.append({
            'planeta':   nombre,
            'altitud':   round(alt.degrees, 1),
            'azimut':    round(az.degrees, 1),
            'direccion': direccion(az.degrees),
            'magnitud':  mag,
            'visible':   True,
        })
    resultado.sort(key=lambda x: x['altitud'], reverse=True)
    return resultado


def estado_cielo(t=None):
    t = TS.now() if t is None else t
    alt_sol = float(altura_sol(t))
    return {'altura_sol': round(alt_sol, 1), 'condicion': condicion_cielo(alt_sol)}


def planetas_visibles(t=None):
    """Planetas visibles AHORA. Lista vacía si es de día o no hay ninguno arriba."""
    t = TS.now() if t is None else t
    if altura_sol(t) > SOL_MAX:
        return []
    return _posiciones(t)


def proxima_ventana(horas=36, desde=None):
    """Primer momento (cada 15 min) en que el cielo está oscuro y hay algún planeta arriba."""
    inicio = TS.now() if desde is None else desde
    pasos  = np.arange(1, int(horas * 60 / PASO_MINUTOS) + 1) * PASO_MINUTOS
    tiempos = TS.tt_jd(inicio.tt + pasos / 1440.0)

    alt_sol, _, _ = OBSERVADOR.at(tiempos).observe(SOL).apparent().altaz()
    oscuro = alt_sol.degrees <= SOL_MAX

    alguno_arriba = np.zeros(len(pasos), dtype=bool)
    for cuerpo in PLANETAS.values():
        alt, _, _ = OBSERVADOR.at(tiempos).observe(cuerpo).apparent().altaz()
        alguno_arriba |= alt.degrees >= ALTURA_MIN_PLANETA

    indices = np.nonzero(oscuro & alguno_arriba)[0]
    if not len(indices):
        return None
    i = int(indices[0])
    t = tiempos[i]
    minutos = int(pasos[i])
    return {
        'en_horas':   round(minutos / 60, 1),
        'en_minutos': minutos,
        'hora_local': a_local(t.utc_datetime()).strftime('%H:%M'),
        'planetas':   _posiciones(t),
    }


if __name__ == '__main__':
    ahora = planetas_visibles()
    print(f"\nCielo en {CITY}: {estado_cielo()}")
    if ahora:
        for p in ahora:
            print(f"  {p['planeta']:<10} {p['altitud']:>5.1f}°  {p['direccion']:<3} mag {p['magnitud']}")
    else:
        v = proxima_ventana()
        print(f"  Ninguno ahora. Próxima ventana: {v['hora_local']} → {[p['planeta'] for p in v['planetas']]}" if v else '  Ninguno en 36 h')
