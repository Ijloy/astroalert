import requests
from datetime import datetime, timezone, timedelta
from config import LAT, LON, CITY

# Cometas conocidos actualmente activos — fuente: JPL/MPC
COMETAS_CONOCIDOS = [
    {
        "id": "C2024_G3",
        "nombre": "C/2024 G3 (ATLAS)",
        "descripcion": "Cometa descubierto en abril 2024 por el programa ATLAS. Alcanzó su perihelio en enero 2026.",
        "magnitud_pico": 2.0,
        "fecha_perihelio": "2026-01-13",
        "activo": True,
    },
    {
        "id": "C2023_A3",
        "nombre": "C/2023 A3 (Tsuchinshan-ATLAS)",
        "descripcion": "Uno de los cometas más brillantes de la década. Visible a simple vista en octubre 2024.",
        "magnitud_pico": 0.2,
        "fecha_perihelio": "2024-09-27",
        "activo": False,
    },
    {
        "id": "12P",
        "nombre": "12P/Pons-Brooks",
        "descripcion": "Cometa periódico de 71 años. Apodado el cometa del diablo por su forma de cuernos.",
        "magnitud_pico": 4.5,
        "fecha_perihelio": "2024-04-21",
        "activo": False,
    },
    {
        "id": "C2025_N1",
        "nombre": "C/2025 N1 (ATLAS)",
        "descripcion": "Cometa descubierto en 2025, actualmente en aproximación al sol.",
        "magnitud_pico": 6.0,
        "fecha_perihelio": "2026-11-15",
        "activo": True,
    },
    {
        "id": "29P",
        "nombre": "29P/Schwassmann-Wachmann",
        "descripcion": "Cometa conocido por sus erupciones periódicas de gas y polvo.",
        "magnitud_pico": 9.0,
        "fecha_perihelio": "2026-03-01",
        "activo": True,
    },
]

def _horizons_cometa(nombre_horizons):
    """Consulta posición actual de un cometa via JPL Horizons."""
    try:
        ahora = datetime.now(timezone.utc)
        fin   = ahora + timedelta(minutes=1)
        params = {
            'format':     'json',
            'COMMAND':    f"'{nombre_horizons}'",
            'OBJ_DATA':   'NO',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'OBSERVER',
            'CENTER':     '500@399',
            'START_TIME': f"'{ahora.strftime('%Y-%b-%d %H:%M')}'",
            'STOP_TIME':  f"'{fin.strftime('%Y-%b-%d %H:%M')}'",
            'STEP_SIZE':  '1m',
            'QUANTITIES': '9',  # brillo visual
        }
        r    = requests.get('https://ssd.jpl.nasa.gov/api/horizons.api', params=params, timeout=15)
        data = r.json().get('result', '')
        soe  = data.find('$$SOE')
        eoe  = data.find('$$EOE')
        if soe == -1:
            return None
        linea  = data[soe:eoe].split('\n')[1].strip()
        partes = linea.split()
        if len(partes) >= 5:
            return {'magnitud': partes[4]}
    except:
        pass
    return None

def obtener_cometas():
    ahora    = datetime.now(timezone.utc)
    resultado = []

    for c in COMETAS_CONOCIDOS:
        fecha_peri = datetime.strptime(c['fecha_perihelio'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        dias_desde = (ahora - fecha_peri).days
        dias_hasta = (fecha_peri - ahora).days

        if dias_hasta > 0:
            estado    = 'próximo'
            tiempo_txt = f"Perihelio en {dias_hasta} días"
        elif dias_desde < 180:
            estado    = 'activo'
            tiempo_txt = f"Perihelio hace {dias_desde} días"
        else:
            estado    = 'pasado'
            tiempo_txt = f"Perihelio hace {dias_desde} días"

        resultado.append({
            'id':              c['id'],
            'nombre':          c['nombre'],
            'descripcion':     c['descripcion'],
            'magnitud_pico':   c['magnitud_pico'],
            'fecha_perihelio': fecha_peri.strftime('%d/%m/%Y'),
            'estado':          estado,
            'tiempo':          tiempo_txt,
            'visible_binoculares': c['magnitud_pico'] < 8.0,
            'visible_simple_vista': c['magnitud_pico'] < 5.0,
        })

    resultado.sort(key=lambda x: (x['estado'] != 'activo', x['magnitud_pico']))
    return resultado

if __name__ == '__main__':
    print('\nCometas:\n')
    for c in obtener_cometas():
        vis = '👁 simple vista' if c['visible_simple_vista'] else ('🔭 binoculares' if c['visible_binoculares'] else '📡 telescopio')
        print(f"  {c['nombre']:<35}  {c['estado']:<8}  mag {c['magnitud_pico']}  {vis}")
        print(f"    {c['tiempo']}")
        