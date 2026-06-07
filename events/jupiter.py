from skyfield.api import Topos, load
from datetime import datetime, timezone, timedelta
import os

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_loader   = load.__class__(BASE_DIR)
TS        = _loader.timescale()
EPH_MAIN  = _loader('de421.bsp')
EPH_JUP   = _loader('jup365.bsp')

LUNAS = {
    'Io':        EPH_JUP[501],
    'Europa':    EPH_JUP[502],
    'Ganimedes': EPH_JUP[503],
    'Calisto':   EPH_JUP[504],
}

JUPITER = EPH_MAIN['jupiter barycenter']
TIERRA  = EPH_MAIN['earth']

def lunas_jupiter():
    ahora = datetime.now(timezone.utc)
    t     = TS.from_datetime(ahora)

    ast_jup     = TIERRA.at(t).observe(JUPITER).apparent()
    ra_j, dec_j, _ = ast_jup.radec()

    resultado = []
    for nombre, luna in LUNAS.items():
        ast_luna        = TIERRA.at(t).observe(luna).apparent()
        ra_l, dec_l, _  = ast_luna.radec()

        diff_ra  = (ra_l.hours - ra_j.hours) * 15
        diff_dec = (dec_l.degrees - dec_j.degrees)

        resultado.append({
            'luna':     nombre,
            'lado':     'Este' if diff_ra > 0 else 'Oeste',
            'distancia_arcsec': round((diff_ra**2 + diff_dec**2)**0.5 * 3600, 1),
            'diff_ra':  round(diff_ra * 3600, 1),
            'diff_dec': round(diff_dec * 3600, 1),
        })

    resultado.sort(key=lambda x: x['distancia_arcsec'])
    return resultado

if __name__ == '__main__':
    print('\nLunas de Júpiter ahora mismo:\n')
    for l in lunas_jupiter():
        print(f"  {l['luna']:<10}  {l['lado']:<6}  distancia: {l['distancia_arcsec']}\"")