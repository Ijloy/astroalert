"""Imagen astronómica del día (APOD) de la NASA.

Usa NASA_API_KEY si está definida; si no, la clave pública DEMO_KEY
(funciona, pero con un límite bajo de peticiones por hora). El resultado
se guarda en memoria unas horas para no consultar a la NASA en cada visita.
"""
import logging
import time

import requests

from config import NASA_API_KEY

log = logging.getLogger(__name__)

APOD_URL   = "https://api.nasa.gov/planetary/apod"
CACHE_SEG  = 6 * 3600
_cache     = {"dato": None, "hasta": 0}


def imagen_del_dia():
    if _cache["dato"] and time.time() < _cache["hasta"]:
        return _cache["dato"]
    try:
        r = requests.get(APOD_URL, params={"api_key": NASA_API_KEY}, timeout=10)
        r.raise_for_status()
        d = r.json()
        # Algunos días el APOD es un video; en ese caso usamos su miniatura si existe.
        url = d.get("url") if d.get("media_type") == "image" else d.get("thumbnail_url")
        dato = {
            "titulo":    d.get("title"),
            "fecha":     d.get("date"),
            "url":       url,
            "autor":     d.get("copyright"),
            "pagina":    f"https://apod.nasa.gov/apod/ap{d['date'][2:].replace('-', '')}.html" if d.get("date") else None,
        }
        _cache.update(dato=dato, hasta=time.time() + CACHE_SEG)
        return dato
    except Exception:
        log.warning("APOD de la NASA no disponible", exc_info=True)
        return _cache["dato"]
