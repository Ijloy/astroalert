from skyfield.api import Topos, load
from datetime import datetime, timezone, timedelta
from math import degrees, acos, sin, cos, radians
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_loader  = load.__class__(BASE_DIR)
TS       = _loader.timescale()
EPH      = _loader('de421.bsp')

PLANETAS = {
    'Mercurio': EPH['mercury'],
    'Venus':    EPH['venus'],
    'Marte':    EPH['mars'],
    'Jupiter':  EPH['jupiter barycenter'],
    'Saturno':  EPH['saturn barycenter'],
}

def _separacion(cuerpo1, cuerpo2, t):
    tierra = EPH['earth']
    a1 = tierra.at(t).observe(cuerpo1).apparent()
    a2 = tierra.at(t).observe(cuerpo2).apparent()
    ra1, dec1, _ = a1.radec()
    ra2, dec2, _ = a2.radec()
    sep = acos(min(1.0, sin(dec1.radians) * sin(dec2.radians) +
                cos(dec1.radians) * cos(dec2.radians) *
                cos(ra1.radians - ra2.radians)))
    return degrees(sep)

def proximas_conjunciones(dias=90):
    ahora  = datetime.now(timezone.utc)
    ahora_ts = ahora.timestamp()
    nombres = list(PLANETAS.keys())
    conjunciones = []

    for i in range(len(nombres)):
        for j in range(i + 1, len(nombres)):
            n1, n2 = nombres[i], nombres[j]
            c1, c2 = PLANETAS[n1], PLANETAS[n2]

            min_sep   = 999
            min_fecha = None

            for d in range(dias):
                dt = ahora + timedelta(days=d)
                t  = TS.from_datetime(dt)
                sep = _separacion(c1, c2, t)
                if sep < min_sep:
                    min_sep   = sep
                    min_fecha = dt

            if min_sep < 5.0:
                dt_local = min_fecha - timedelta(hours=5)
                diff     = min_fecha.timestamp() - ahora_ts
                dias_r   = int(diff // 86400)
                horas_r  = int((diff % 86400) // 3600)
                conjunciones.append({
                    'planeta1':    n1,
                    'planeta2':    n2,
                    'separacion':  round(min_sep, 2),
                    'fecha_local': dt_local.strftime('%d/%m/%Y'),
                    'timestamp':   min_fecha.timestamp(),
                    'cuenta_regresiva': {
                        'dias':  dias_r,
                        'horas': horas_r,
                        'texto': f"En {dias_r}d {horas_r}h"
                    }
                })

    conjunciones.sort(key=lambda x: x['separacion'])
    return conjunciones

if __name__ == '__main__':
    print('\nPróximas conjunciones planetarias (próximos 90 días):\n')
    conj = proximas_conjunciones()
    if not conj:
        print('  Ninguna conjunción notable en los próximos 90 días.')
    else:
        for c in conj:
            cr = c['cuenta_regresiva']['texto']
            print(f"  {c['planeta1']} + {c['planeta2']:<10}  separación: {c['separacion']}°  —  {c['fecha_local']}  ({cr})")