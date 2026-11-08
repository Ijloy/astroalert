"""Oposiciones: cuando un planeta exterior queda opuesto al Sol.

Ese día sale al anochecer, se ve toda la noche y está en su brillo máximo.
Antes la elongación se calculaba solo con la ascensión recta (ignorando la
declinación) y en pasos de 2 días. Ahora se usa la función de Skyfield
almanac.oppositions_conjunctions, que da el instante exacto.
"""
from datetime import datetime, timezone, timedelta

from skyfield import almanac
from skyfield.magnitudelib import planetary_magnitude

from events.efemerides import TS, EPH, TIERRA, SOL, CITY, a_local, cuenta_regresiva, cache_ttl

PLANETAS_EXTERIORES = {
    'Marte':   EPH['mars'],
    'Júpiter': EPH['jupiter barycenter'],
    'Saturno': EPH['saturn barycenter'],
    'Urano':   EPH['uranus barycenter'],
    'Neptuno': EPH['neptune barycenter'],
}

DIAS_ADELANTE = 800   # Marte tiene oposición cada ~26 meses
A_SIMPLE_VISTA = 5.0  # en una ciudad casi nada más débil que mag 5 se ve a simple vista


def calcular_oposiciones(desde):
    """Próxima oposición de cada planeta exterior a partir de `desde` (datetime UTC)."""
    t0 = TS.from_datetime(desde - timedelta(days=1))
    t1 = TS.from_datetime(desde + timedelta(days=DIAS_ADELANTE))
    eventos = []
    for nombre, planeta in PLANETAS_EXTERIORES.items():
        tiempos, tipos = almanac.find_discrete(t0, t1, almanac.oppositions_conjunctions(EPH, planeta))
        for t, tipo in zip(tiempos, tipos, strict=True):
            if tipo != 1:      # 1 = oposición, 0 = conjunción con el Sol
                continue
            obs  = TIERRA.at(t)
            ast  = obs.observe(planeta).apparent()
            elong = ast.separation_from(obs.observe(SOL).apparent()).degrees
            mag  = round(float(planetary_magnitude(obs.observe(planeta))), 1)
            eventos.append({
                'planeta':      nombre,
                'fecha_utc':    t.utc_datetime(),
                'elongacion':   round(float(elong), 1),
                'distancia_ua': round(float(ast.distance().au), 3),
                'magnitud':     mag,
                'simple_vista': mag <= A_SIMPLE_VISTA,
            })
            break              # solo la próxima de cada planeta
    eventos.sort(key=lambda e: e['fecha_utc'])
    return eventos


@cache_ttl(12 * 3600)
def _calcular():
    return calcular_oposiciones(datetime.now(timezone.utc))


def proximas_oposiciones():
    ahora = datetime.now(timezone.utc)
    resultado = []
    for e in _calcular():
        if e['fecha_utc'] < ahora - timedelta(days=1):
            continue
        como = 'visible a simple vista' if e['simple_vista'] else 'necesitas binoculares o telescopio'
        cr = cuenta_regresiva(e['fecha_utc'])
        cr['texto'] = f"En {cr['dias']} días" if cr['dias'] > 0 else 'Hoy'
        resultado.append({
            'planeta':      e['planeta'],
            'fecha_local':  a_local(e['fecha_utc']).strftime('%d/%m/%Y'),
            'timestamp':    e['fecha_utc'].timestamp(),
            'elongacion':   e['elongacion'],
            'distancia_ua': e['distancia_ua'],
            'magnitud':     e['magnitud'],
            'simple_vista': e['simple_vista'],
            'cuenta_regresiva': cr,
            'descripcion':  (f"{e['planeta']} queda opuesto al Sol: sale al anochecer, se ve toda la noche "
                             f"y alcanza su brillo máximo (magnitud {e['magnitud']}, {como})."),
        })
    return resultado


if __name__ == '__main__':
    print(f'\nPróximas oposiciones ({CITY}):\n')
    for o in proximas_oposiciones():
        print(f"  {o['planeta']:<8} {o['fecha_local']}  {o['distancia_ua']} UA  mag {o['magnitud']}  {o['cuenta_regresiva']['texto']}")
