from skyfield.api import Topos, load
from skyfield import eclipselib
from datetime import datetime, timezone, timedelta
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_loader  = load.__class__(BASE_DIR)
TS       = _loader.timescale()
EPH      = _loader('de421.bsp')

# Eclipses solares próximos — fuente: NASA Eclipse Page
ECLIPSES_SOLARES = [
    {'fecha': '2026-08-12 17:47', 'subtipo': 'Total',   'visible_quito': False},
    {'fecha': '2027-02-06 16:00', 'subtipo': 'Anular',  'visible_quito': False},
    {'fecha': '2027-08-02 10:07', 'subtipo': 'Total',   'visible_quito': True},
    {'fecha': '2028-01-26 15:08', 'subtipo': 'Anular',  'visible_quito': False},
    {'fecha': '2028-07-22 02:56', 'subtipo': 'Total',   'visible_quito': False},
]

def proximos_eclipses(meses=24):
    ahora  = datetime.now(timezone.utc)
    inicio = TS.from_datetime(ahora)
    fin    = TS.from_datetime(ahora + timedelta(days=meses * 30))

    eclipses = []

    # Eclipses lunares con Skyfield
    try:
        tiempos, tipos, _ = eclipselib.lunar_eclipses(inicio, fin, EPH)
        nombres = {0: 'Penumbral', 1: 'Parcial', 2: 'Total'}
        for t, tipo in zip(tiempos, tipos):
            dt = t.utc_datetime()
            dt_local = dt - timedelta(hours=5)
            eclipses.append({
                'tipo':          'Lunar',
                'subtipo':       nombres.get(tipo, 'Desconocido'),
                'fecha_utc':     dt.strftime('%Y-%m-%d %H:%M UTC'),
                'fecha_local':   dt_local.strftime('%d/%m/%Y %H:%M'),
                'timestamp':     dt.timestamp(),
                'visible_quito': True,
            })
    except Exception as e:
        print(f"Error eclipses lunares: {e}")

    # Eclipses solares desde lista NASA
    for es in ECLIPSES_SOLARES:
        dt = datetime.strptime(es['fecha'], '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc)
        if dt > ahora:
            dt_local = dt - timedelta(hours=5)
            eclipses.append({
                'tipo':          'Solar',
                'subtipo':       es['subtipo'],
                'fecha_utc':     dt.strftime('%Y-%m-%d %H:%M UTC'),
                'fecha_local':   dt_local.strftime('%d/%m/%Y %H:%M'),
                'timestamp':     dt.timestamp(),
                'visible_quito': es['visible_quito'],
            })

    eclipses.sort(key=lambda x: x['timestamp'])

    # Cuenta regresiva
    ahora_ts = ahora.timestamp()
    for e in eclipses:
        diff  = e['timestamp'] - ahora_ts
        dias  = int(diff // 86400)
        horas = int((diff % 86400) // 3600)
        mins  = int((diff % 3600) // 60)
        e['cuenta_regresiva'] = {
            'dias':  dias,
            'horas': horas,
            'mins':  mins,
            'texto': f"En {dias}d {horas}h {mins}m"
        }

    return eclipses

if __name__ == '__main__':
    print('\nPróximos eclipses:\n')
    for e in proximos_eclipses():
        cr  = e['cuenta_regresiva']['texto']
        vis = '✓ visible desde Quito' if e['visible_quito'] else '  no visible desde Quito'
        print(f"  {e['tipo']:<6} {e['subtipo']:<10}  {e['fecha_local']}  —  {cr}  {vis}")