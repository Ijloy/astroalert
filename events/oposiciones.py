from skyfield.api import Topos, load
from datetime import datetime, timezone, timedelta
from config import LAT, LON, ALT, CITY
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_loader  = load.__class__(BASE_DIR)
TS       = _loader.timescale()
EPH      = _loader('de421.bsp')

TIERRA = EPH['earth']
SOL    = EPH['sun']

PLANETAS_OPOSICION = {
    'Marte':   EPH['mars'],
    'Júpiter': EPH['jupiter barycenter'],
    'Saturno': EPH['saturn barycenter'],
    'Urano':   EPH['uranus barycenter'],
    'Neptuno': EPH['neptune barycenter'],
}

def _elongacion(planeta, t):
    """Calcula la elongación solar de un planeta en grados."""
    obs      = TIERRA.at(t)
    ast_p    = obs.observe(planeta).apparent()
    ast_sol  = obs.observe(SOL).apparent()
    ra_p,  dec_p,  _ = ast_p.radec()
    ra_s,  dec_s,  _ = ast_sol.radec()
    from math import acos, sin, cos, radians, degrees
    diff = abs(ra_p.hours - ra_s.hours) * 15
    if diff > 180: diff = 360 - diff
    return diff

def _distancia_ua(planeta, t):
    ast  = TIERRA.at(t).observe(planeta)
    _, _, dist = ast.apparent().altaz()
    _, _, dist = TIERRA.at(t).observe(planeta).radec()
    return None

def proximas_oposiciones(dias=365):
    ahora    = datetime.now(timezone.utc)
    ahora_ts = ahora.timestamp()
    resultado = []

    for nombre, planeta in PLANETAS_OPOSICION.items():
        max_elong    = 0
        fecha_oposi  = None
        elong_actual = 0

        for d in range(0, dias, 2):
            dt  = ahora + timedelta(days=d)
            t   = TS.from_datetime(dt)
            elong = _elongacion(planeta, t)

            if elong > max_elong:
                max_elong   = elong
                fecha_oposi = dt
                elong_actual = elong

        if max_elong > 160:
            dt_local = fecha_oposi - timedelta(hours=5)
            diff     = fecha_oposi.timestamp() - ahora_ts
            dias_r   = int(diff // 86400)

            # Calcular distancia aproximada en UA
            t_oposi = TS.from_datetime(fecha_oposi)
            ast     = TIERRA.at(t_oposi).observe(planeta)
            ra, dec, dist = ast.apparent().radec()

            resultado.append({
                'planeta':      nombre,
                'fecha_local':  dt_local.strftime('%d/%m/%Y'),
                'timestamp':    fecha_oposi.timestamp(),
                'elongacion':   round(max_elong, 1),
                'distancia_ua': round(dist.au, 3),
                'cuenta_regresiva': {
                    'dias':  dias_r,
                    'texto': f"En {dias_r} días"
                },
                'descripcion': f"{nombre} estará en su punto más cercano a la Tierra — mejor noche del año para observarlo."
            })

    resultado.sort(key=lambda x: x['timestamp'])
    return resultado

if __name__ == '__main__':
    print('\nPróximas oposiciones planetarias:\n')
    for o in proximas_oposiciones():
        print(f"  {o['planeta']:<10}  {o['fecha_local']}  —  {o['cuenta_regresiva']['texto']}  —  {o['distancia_ua']} UA")