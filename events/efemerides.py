"""Recursos astronómicos compartidos.

Antes cada módulo (sky, eclipses, conjunciones, oposiciones) cargaba su
propia copia de las efemérides DE421 (~16 MB en memoria cada una). Ahora se
cargan una sola vez aquí y todos los módulos las importan.
"""
import os
import time
import functools
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from skyfield.api import Loader, wgs84

from config import LAT, LON, ALT, CITY, TZ_NAME

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_loader = Loader(BASE_DIR)
TS      = _loader.timescale()
EPH     = _loader('de421.bsp')   # cubre 1899–2053

TIERRA = EPH['earth']
SOL    = EPH['sun']
LUNA   = EPH['moon']

# Observador en la superficie (latitud, longitud y altura de la ciudad configurada)
SITIO      = wgs84.latlon(LAT, LON, elevation_m=ALT)
OBSERVADOR = TIERRA + SITIO

ZONA = ZoneInfo(TZ_NAME)

# Planetas visibles a simple vista
PLANETAS = {
    'Mercurio': EPH['mercury'],
    'Venus':    EPH['venus'],
    'Marte':    EPH['mars'],
    'Júpiter':  EPH['jupiter barycenter'],
    'Saturno':  EPH['saturn barycenter'],
}

DIRECCIONES = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']


def direccion(azimut_grados):
    return DIRECCIONES[round(azimut_grados / 45) % 8]


def a_local(dt_utc):
    """Convierte un datetime UTC a la hora local de la ciudad configurada."""
    return dt_utc.astimezone(ZONA)


def cuenta_regresiva(dt_utc):
    """Días/horas/minutos que faltan hasta dt_utc (calculado en cada petición)."""
    diff = max(0, (dt_utc - datetime.now(timezone.utc)).total_seconds())
    dias  = int(diff // 86400)
    horas = int((diff % 86400) // 3600)
    mins  = int((diff % 3600) // 60)
    if dias > 0:
        texto = f"En {dias}d {horas}h"
    elif horas > 0:
        texto = f"En {horas}h {mins}m"
    else:
        texto = f"En {mins} min"
    return {'dias': dias, 'horas': horas, 'mins': mins, 'texto': texto}


def cache_ttl(segundos):
    """Guarda el resultado de una función sin argumentos durante `segundos`.

    Los eventos (eclipses, conjunciones, oposiciones) cambian una vez al día;
    recalcularlos en cada visita costaba 2–3 s por petición.
    """
    def decorador(func):
        estado = {'valor': None, 'hasta': 0.0}

        @functools.wraps(func)
        def envoltura():
            if estado['valor'] is None or time.time() >= estado['hasta']:
                estado['valor'] = func()
                estado['hasta'] = time.time() + segundos
            return estado['valor']

        envoltura.limpiar_cache = lambda: estado.update(valor=None, hasta=0.0)
        return envoltura
    return decorador


__all__ = ['TS', 'EPH', 'TIERRA', 'SOL', 'LUNA', 'SITIO', 'OBSERVADOR', 'ZONA', 'CITY',
           'PLANETAS', 'direccion', 'a_local', 'cuenta_regresiva', 'cache_ttl']
