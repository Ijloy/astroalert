import requests
from datetime import datetime, timezone, timedelta
from config import LAT, LON, CITY

PLANETAS_NOMBRES = ['Mercurio', 'Venus', 'Marte', 'Jupiter', 'Saturno']

def _grados_a_dir(az):
    dirs = ['N','NE','E','SE','S','SO','O','NO']
    return dirs[round(az / 45) % 8]

def _obtener_planetas_hora(hora_utc):
    resultado = []
    try:
        for planeta in PLANETAS_NOMBRES:
            url = f"https://api.visibleplanets.dev/v3?latitude={LAT}&longitude={LON}&time={hora_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                continue
            data = r.json()
            for p in data.get('data', []):
                if p['name'] == planeta and p['altitudeDegrees'] > 5:
                    resultado.append({
                        'planeta':   planeta,
                        'altitud':   round(p['altitudeDegrees'], 1),
                        'azimut':    round(p['azimuthDegrees'], 1),
                        'direccion': _grados_a_dir(p['azimuthDegrees']),
                        'visible':   True,
                    })
    except Exception as e:
        print(f"Error obteniendo planetas: {e}")
    resultado.sort(key=lambda x: x['altitud'], reverse=True)
    return resultado

def planetas_visibles():
    return _obtener_planetas_hora(datetime.now(timezone.utc))

def proxima_ventana():
    for h in range(1, 25):
        futuro = datetime.now(timezone.utc) + timedelta(hours=h)
        planetas = _obtener_planetas_hora(futuro)
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