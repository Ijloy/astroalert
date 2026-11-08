"""Eclipses de Sol y de Luna, con su visibilidad desde la ciudad configurada.

Antes los eclipses solares eran una lista escrita a mano con errores (el total
del 2/8/2027 figuraba como visible desde Quito y el anular del 26/1/2028, que
sí cruza Ecuador, como no visible). Ahora todo se calcula con Skyfield:

* Solares: en cada luna nueva se comprueba si la sombra de la Luna toca la
  Tierra (condición geocéntrica clásica) y luego se simula el cielo minuto a
  minuto desde la ciudad para saber si se ve, de qué tipo, cuánto del Sol se
  cubre y a qué hora.
* Lunares: skyfield.eclipselib, y se marca visible si la Luna está sobre el
  horizonte en el máximo.
"""
from datetime import timedelta, datetime, timezone

import numpy as np
from skyfield import almanac, eclipselib

from events.efemerides import TS, EPH, TIERRA, SOL, LUNA, OBSERVADOR, CITY, a_local, cuenta_regresiva, cache_ttl

R_SOL_KM    = 696_000.0
R_LUNA_KM   = 1_737.4
R_TIERRA_KM = 6_378.14
UA_KM       = 149_597_870.7

MESES_ADELANTE = 30
VENTANA_MIN    = 240          # ± minutos alrededor de la luna nueva a revisar

NOMBRES_LUNAR = {0: 'Penumbral', 1: 'Parcial', 2: 'Total'}


def _semidiametro(radio_km, distancia_km):
    return np.degrees(np.arcsin(radio_km / distancia_km))


def _tiempos_alrededor(t_centro, minutos, paso_seg):
    offsets = np.arange(-minutos * 60, minutos * 60 + paso_seg, paso_seg) / 86400.0
    return TS.tt_jd(t_centro.tt + offsets)


def _eclipse_solar_global(t_luna_nueva):
    """¿Hay eclipse solar en algún lugar de la Tierra? Devuelve (tipo, t_max) o None."""
    tiempos = _tiempos_alrededor(t_luna_nueva, VENTANA_MIN, 60)
    obs  = TIERRA.at(tiempos)
    sol  = obs.observe(SOL).apparent()
    luna = obs.observe(LUNA).apparent()
    sep  = sol.separation_from(luna).degrees
    i    = int(np.argmin(sep))

    d_sol  = sol.distance().km[i]
    d_luna = luna.distance().km[i]
    s_sol, s_luna = _semidiametro(R_SOL_KM, d_sol), _semidiametro(R_LUNA_KM, d_luna)
    par_luna = np.degrees(np.arcsin(R_TIERRA_KM / d_luna))
    par_sol  = np.degrees(np.arcsin(R_TIERRA_KM / d_sol))

    if sep[i] > s_sol + s_luna + par_luna - par_sol:
        return None   # la penumbra no toca la Tierra

    # Eclipse central (el eje de la sombra cruza la Tierra): total o anular.
    if sep[i] < par_luna - par_sol:
        # Visto desde el punto subsolar la Luna está ~1 radio terrestre más cerca.
        s_luna_cerca = _semidiametro(R_LUNA_KM, d_luna - R_TIERRA_KM)
        tipo = 'Total' if s_luna_cerca > s_sol else 'Anular'
    else:
        tipo = 'Parcial'
    return tipo, tiempos[i]


def _circunstancias_locales(t_centro, observador=OBSERVADOR):
    """Cómo se ve el eclipse desde un lugar (por defecto, la ciudad configurada)."""
    tiempos = _tiempos_alrededor(t_centro, VENTANA_MIN, 30)
    obs  = observador.at(tiempos)
    sol  = obs.observe(SOL).apparent()
    luna = obs.observe(LUNA).apparent()

    alt_sol, _, _ = sol.altaz()
    sep    = sol.separation_from(luna).degrees
    s_sol  = _semidiametro(R_SOL_KM, sol.distance().km)
    s_luna = _semidiametro(R_LUNA_KM, luna.distance().km)

    solapan = (sep < s_sol + s_luna) & (alt_sol.degrees > -0.833)
    if not solapan.any():
        return None

    idx = np.nonzero(solapan)[0]
    i   = idx[np.argmin(sep[idx])]
    magnitud = (s_sol[i] + s_luna[i] - sep[i]) / (2 * s_sol[i])

    tipo_local = 'Parcial'
    duracion_s = None
    if sep[i] < abs(s_luna[i] - s_sol[i]):
        tipo_local = 'Total' if s_luna[i] > s_sol[i] else 'Anular'
        # Duración de la fase central, con resolución de 1 s alrededor del máximo
        fino = _tiempos_alrededor(tiempos[i], 8, 1)
        o2 = observador.at(fino)
        so, lu = o2.observe(SOL).apparent(), o2.observe(LUNA).apparent()
        central = so.separation_from(lu).degrees < np.abs(
            _semidiametro(R_LUNA_KM, lu.distance().km) - _semidiametro(R_SOL_KM, so.distance().km))
        duracion_s = int(central.sum())

    return {
        'tipo':        tipo_local,
        'magnitud':    round(float(magnitud), 3),
        'inicio':      tiempos[idx[0]].utc_datetime(),
        'maximo':      tiempos[i].utc_datetime(),
        'fin':         tiempos[idx[-1]].utc_datetime(),
        'altura_sol':  round(float(alt_sol.degrees[i]), 1),
        'duracion_central_s': duracion_s,
    }


def _eclipses_solares(t0, t1, observador=OBSERVADOR):
    tiempos, fases = almanac.find_discrete(t0, t1, almanac.moon_phases(EPH))
    lunas_nuevas = [t for t, f in zip(tiempos, fases, strict=True) if f == 0]
    eventos = []
    for t_nueva in lunas_nuevas:
        g = _eclipse_solar_global(t_nueva)
        if not g:
            continue
        tipo, t_max = g
        local = _circunstancias_locales(t_max, observador)
        eventos.append({
            'tipo':      'Solar',
            'subtipo':   tipo,
            'fecha_utc': (local['maximo'] if local else t_max.utc_datetime()),
            'visible_local': local is not None,
            'local':     local,
        })
    return eventos


def _eclipses_lunares(t0, t1):
    tiempos, tipos, _ = eclipselib.lunar_eclipses(t0, t1, EPH)
    eventos = []
    for t, tipo in zip(tiempos, tipos, strict=True):
        alt, _, _ = OBSERVADOR.at(t).observe(LUNA).apparent().altaz()
        visible = bool(alt.degrees > 0)
        eventos.append({
            'tipo':      'Lunar',
            'subtipo':   NOMBRES_LUNAR.get(int(tipo), 'Desconocido'),
            'fecha_utc': t.utc_datetime(),
            'visible_local': visible,
            'local':     {'altura_luna': round(float(alt.degrees), 1)},
        })
    return eventos


@cache_ttl(6 * 3600)
def _calcular():
    ahora = datetime.now(timezone.utc)
    t0 = TS.from_datetime(ahora - timedelta(hours=6))
    t1 = TS.from_datetime(ahora + timedelta(days=MESES_ADELANTE * 30.44))
    eventos = _eclipses_solares(t0, t1) + _eclipses_lunares(t0, t1)
    eventos.sort(key=lambda e: e['fecha_utc'])
    return eventos


def _descripcion(e):
    if e['tipo'] == 'Lunar':
        if not e['visible_local']:
            return f"La Luna estará bajo el horizonte de {CITY} durante el máximo."
        if e['subtipo'] == 'Penumbral':
            return "La Luna se oscurece levemente; es un cambio sutil, difícil de notar a simple vista."
        return f"Visible desde {CITY} con la Luna a {e['local']['altura_luna']}° de altura."
    loc = e['local']
    if not loc:
        return f"No se verá desde {CITY}."
    if loc['tipo'] in ('Anular', 'Total'):
        dur = loc['duracion_central_s']
        txt = f"¡Eclipse {loc['tipo'].lower()} desde {CITY}!"
        if dur:
            txt += f" La fase {loc['tipo'].lower()} dura {dur // 60} min {dur % 60} s."
        return txt
    return f"Parcial desde {CITY}: la Luna cubrirá el {round(loc['magnitud'] * 100)}% del diámetro del Sol."


def proximos_eclipses():
    ahora = datetime.now(timezone.utc)
    resultado = []
    for e in _calcular():
        if e['fecha_utc'] < ahora:
            continue
        local = dict(e['local']) if e['local'] else None
        if local and e['tipo'] == 'Solar':
            for k in ('inicio', 'maximo', 'fin'):
                local[k] = a_local(local[k]).strftime('%H:%M')
        resultado.append({
            'tipo':          e['tipo'],
            'subtipo':       e['subtipo'],
            'fecha_utc':     e['fecha_utc'].strftime('%Y-%m-%d %H:%M UTC'),
            'fecha_local':   a_local(e['fecha_utc']).strftime('%d/%m/%Y %H:%M'),
            'timestamp':     e['fecha_utc'].timestamp(),
            'visible_local': e['visible_local'],
            'visible_quito': e['visible_local'],   # nombre antiguo, se mantiene por compatibilidad
            'local':         local,
            'descripcion':   _descripcion(e),
            'cuenta_regresiva': cuenta_regresiva(e['fecha_utc']),
        })
    return resultado


if __name__ == '__main__':
    print(f'\nPróximos eclipses ({CITY}):\n')
    for e in proximos_eclipses():
        vis = '✓' if e['visible_local'] else '✗'
        print(f"  {vis} {e['tipo']:<6} {e['subtipo']:<10} {e['fecha_local']}  {e['descripcion']}")
