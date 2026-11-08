"""Cometas destacados recientes.

La lista anterior tenía fechas de perihelio incorrectas (C/2024 G3 en 2026 en
vez del 13/01/2025; C/2025 N1 como cometa "en aproximación" en 2026, cuando es
3I/ATLAS, el tercer objeto interestelar, con perihelio el 29/10/2025) y
marcaba cometas como "activos" sin base.

Esta lista es curada a mano: solo datos verificados, con su fuente. El estado
(próximo / reciente / pasado) se calcula a partir de las fechas.
Integración futura: consultar JPL SBDB para obtener cometas en tiempo real.
"""
from datetime import datetime, timezone

ACTUALIZADO = "2026-11-08"

COMETAS_CONOCIDOS = [
    {
        "id": "C2024_G3",
        "nombre": "C/2024 G3 (ATLAS)",
        "descripcion": ("El \"Gran Cometa de 2025\". Pasó a solo 0,09 UA del Sol y llegó a magnitud −3,8; "
                        "se vio mejor desde el hemisferio sur. Su núcleo se desintegró después del perihelio."),
        "magnitud_pico": -3.8,
        "fecha_perihelio": "2025-01-13",
        "fuente": "https://en.wikipedia.org/wiki/C/2024_G3_(ATLAS)",
    },
    {
        "id": "3I_ATLAS",
        "nombre": "3I/ATLAS (C/2025 N1)",
        "descripcion": ("El tercer objeto interestelar conocido, después de ʻOumuamua y Borisov. "
                        "Descubierto el 1 de julio de 2025 desde Chile; viene de fuera del sistema solar "
                        "y no volverá. Solo se pudo observar con telescopios."),
        "magnitud_pico": None,
        "fecha_perihelio": "2025-10-29",
        "fuente": "https://www.timeanddate.com/news/astronomy/comet-3i-atlas",
    },
    {
        "id": "C2023_A3",
        "nombre": "C/2023 A3 (Tsuchinshan-ATLAS)",
        "descripcion": ("El \"Gran Cometa de 2024\". Cerca del perihelio se observó con binoculares "
                        "alrededor de magnitud −3, y en octubre de 2024 se vio a simple vista al atardecer "
                        "con una cola larga."),
        "magnitud_pico": -3.0,
        "fecha_perihelio": "2024-09-27",
        "fuente": "https://en.wikipedia.org/wiki/C/2023_A3_(Tsuchinshan%E2%80%93ATLAS)",
    },
    {
        "id": "12P",
        "nombre": "12P/Pons-Brooks",
        "descripcion": ("Cometa periódico que vuelve cada ~71 años. Apodado \"cometa del diablo\" por la "
                        "forma de cuernos que tomó tras sus estallidos."),
        "magnitud_pico": 4.5,
        "fecha_perihelio": "2024-04-21",
        "fuente": "https://en.wikipedia.org/wiki/12P/Pons%E2%80%93Brooks",
    },
]

DIAS_RECIENTE = 180


def _estado(fecha_peri, ahora):
    dias = (fecha_peri - ahora).days
    if dias > 0:
        return 'próximo', f"Perihelio en {dias} días"
    hace = -dias
    return ('reciente' if hace < DIAS_RECIENTE else 'pasado'), f"Perihelio hace {hace} días"


def obtener_cometas():
    ahora = datetime.now(timezone.utc)
    resultado = []
    for c in COMETAS_CONOCIDOS:
        fecha_peri = datetime.strptime(c['fecha_perihelio'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        estado, tiempo = _estado(fecha_peri, ahora)
        mag = c['magnitud_pico']
        resultado.append({
            'id':              c['id'],
            'nombre':          c['nombre'],
            'descripcion':     c['descripcion'],
            'magnitud_pico':   mag,
            'fecha_perihelio': fecha_peri.strftime('%d/%m/%Y'),
            'timestamp':       fecha_peri.timestamp(),
            'estado':          estado,
            'tiempo':          tiempo,
            'visible_simple_vista': mag is not None and mag < 5.0,
            'visible_binoculares':  mag is not None and mag < 8.0,
            'fuente':          c['fuente'],
            'actualizado':     ACTUALIZADO,
        })
    # Primero los próximos, luego los más recientes
    resultado.sort(key=lambda x: (x['estado'] != 'próximo', -x['timestamp']))
    return resultado


if __name__ == '__main__':
    for c in obtener_cometas():
        print(f"  {c['nombre']:<32} {c['estado']:<9} {c['tiempo']}")
