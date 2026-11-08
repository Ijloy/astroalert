"""Conjunciones planetarias: dos planetas que se ven muy juntos en el cielo.

Mejoras respecto a la versión anterior:
* Se buscan TODOS los acercamientos (mínimos locales), no solo el mínimo de
  cada par en 90 días, y se refinan a la hora exacta.
* Se calcula la distancia al Sol: una conjunción a menos de 15° del Sol no se
  puede observar, y ahora se avisa.
* Los resultados se ordenan por fecha (antes, por separación).
* Cálculo vectorizado + caché: de ~2,3 s por petición a una sola vez cada 6 h.
"""
from datetime import datetime, timezone, timedelta
from itertools import combinations

import numpy as np

from events.efemerides import TS, TIERRA, SOL, PLANETAS, CITY, a_local, cuenta_regresiva, cache_ttl

DIAS_ADELANTE     = 120
SEPARACION_MAX    = 3.0    # grados: más allá no se percibe como "conjunción"
ELONGACION_MIN    = 15.0   # grados: más cerca del Sol, se pierde en su resplandor


def _refinar(c1, c2, t_aprox):
    """Busca el mínimo con resolución de 1 hora en ±1 día."""
    tiempos = TS.tt_jd(t_aprox.tt + np.arange(-24, 25) / 24.0)
    obs = TIERRA.at(tiempos)
    sep = obs.observe(c1).apparent().separation_from(obs.observe(c2).apparent()).degrees
    i = int(np.argmin(sep))
    return tiempos[i], float(sep[i])


@cache_ttl(6 * 3600)
def _calcular():
    ahora   = datetime.now(timezone.utc)
    tiempos = TS.from_datetimes([ahora + timedelta(days=d) for d in range(DIAS_ADELANTE)])
    obs     = TIERRA.at(tiempos)
    pos     = {n: obs.observe(c).apparent() for n, c in PLANETAS.items()}
    eventos = []

    for n1, n2 in combinations(PLANETAS, 2):
        sep = pos[n1].separation_from(pos[n2]).degrees
        # mínimos locales (incluye los extremos del intervalo)
        for i in range(len(sep)):
            izq = sep[i - 1] if i > 0 else np.inf
            der = sep[i + 1] if i < len(sep) - 1 else np.inf
            if sep[i] <= izq and sep[i] <= der and sep[i] < SEPARACION_MAX + 1:
                t_min, s_min = _refinar(PLANETAS[n1], PLANETAS[n2], tiempos[i])
                if s_min > SEPARACION_MAX:
                    continue
                o = TIERRA.at(t_min)
                elong = o.observe(SOL).apparent().separation_from(o.observe(PLANETAS[n1]).apparent()).degrees
                eventos.append({
                    'planeta1':   n1,
                    'planeta2':   n2,
                    'separacion': round(s_min, 2),
                    'fecha_utc':  t_min.utc_datetime(),
                    'elongacion_sol': round(float(elong), 1),
                    'observable': bool(elong >= ELONGACION_MIN),
                })

    eventos.sort(key=lambda e: e['fecha_utc'])
    return eventos


def proximas_conjunciones():
    ahora = datetime.now(timezone.utc)
    resultado = []
    for e in _calcular():
        if e['fecha_utc'] < ahora - timedelta(hours=12):
            continue
        nota = (f"A {e['elongacion_sol']}° del Sol: buena oportunidad para observar."
                if e['observable'] else
                f"Solo a {e['elongacion_sol']}° del Sol: se pierde en su resplandor, difícil de observar.")
        resultado.append({
            'planeta1':    e['planeta1'],
            'planeta2':    e['planeta2'],
            'separacion':  e['separacion'],
            'fecha_local': a_local(e['fecha_utc']).strftime('%d/%m/%Y'),
            'hora_local':  a_local(e['fecha_utc']).strftime('%H:%M'),
            'timestamp':   e['fecha_utc'].timestamp(),
            'elongacion_sol': e['elongacion_sol'],
            'observable':  e['observable'],
            'nota':        nota,
            'cuenta_regresiva': cuenta_regresiva(e['fecha_utc']),
        })
    return resultado


if __name__ == '__main__':
    print(f'\nConjunciones (< {SEPARACION_MAX}°) en los próximos {DIAS_ADELANTE} días — {CITY}:\n')
    for c in proximas_conjunciones():
        print(f"  {c['fecha_local']}  {c['planeta1']} + {c['planeta2']:<9} {c['separacion']}°  {c['nota']}")
