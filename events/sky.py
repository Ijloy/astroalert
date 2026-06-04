from skyfield.api import Topos, load
from config import LAT, LON, ALT, CITY
from datetime import datetime, timezone, timedelta
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'skyfield_data')
os.makedirs(DATA_DIR, exist_ok=True)

_loader = load.__class__(DATA_DIR)
TS  = _loader.timescale()
EPH = _loader('de421.bsp')

OBS    = Topos(latitude_degrees=LAT, longitude_degrees=LON, elevation_m=ALT)
TIERRA = EPH['earth']

PLANETAS = {
    'Mercurio': EPH['mercury'],
    'Venus':    EPH['venus'],
    'Marte':    EPH['mars'],
    'Jupiter':  EPH['jupiter barycenter'],
    'Saturno':  EPH['saturn barycenter'],
}

DIRS = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']

def direccion(az):
    return DIRS[round(az / 45) % 8]

def _calcular(t):
    resultado = []
    for nombre, cuerpo in PLANETAS.items():
        ast = (TIERRA + OBS).at(t).observe(cuerpo)
        alt, az, dist = ast.apparent().altaz()
        if alt.degrees > 5:
            resultado.append({
                'planeta':   nombre,
                'altitud':   round(alt.degrees, 1),
                'azimut':    round(az.degrees, 1),
                'direccion': direccion(az.degrees),
                'visible':   True,
            })
    resultado.sort(key=lambda x: x['altitud'], reverse=True)
    return resultado

def planetas_visibles():
    return _calcular(TS.now())

def proxima_ventana():
    for h in range(1, 25):
        futuro = datetime.now(timezone.utc) + timedelta(hours=h)
        t = TS.from_datetime(futuro)
        planetas = _calcular(t)
        if planetas:
            hora_local = futuro - timedelta(hours=5)
            return {
                'en_horas':   h,
                'hora_local': hora_local.strftime('%H:%M'),
                'planetas':   planetas,
            }
    return None

if __name__ == '__main__':
    ahora = planetas_visibles()
    if ahora:
        print(f'\nPlanetas visibles AHORA desde {CITY}:\n')
        for p in ahora:
            print(f"  {p['planeta']:<10}  {p['altitud']:>5.1f}°  direccion: {p['direccion']}")
    else:
        print(f'\nAhora mismo no hay planetas visibles desde {CITY}.')
        ventana = proxima_ventana()
        if ventana:
            print(f"  Proxima ventana: {ventana['hora_local']} (en {ventana['en_horas']}h)")
            print(f"  Planetas: {', '.join(p['planeta'] for p in ventana['planetas'])}")
    print()