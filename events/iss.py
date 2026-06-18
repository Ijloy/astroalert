import requests
from datetime import datetime, timezone
from config import LAT, LON, CITY

ISS_URL = "https://api.wheretheiss.at/v1/satellites/25544"

def posicion_actual():
    """Posición en tiempo real de la ISS."""
    r = requests.get(ISS_URL, timeout=10)
    r.raise_for_status()
    d = r.json()
    return {
        "lat": round(d["latitude"], 4),
        "lon": round(d["longitude"], 4),
        "altitud": round(d["altitude"], 1),
        "velocidad": round(d["velocity"], 1),
        "timestamp": datetime.fromtimestamp(d["timestamp"], tz=timezone.utc)
    }

def distancia_km(lat1, lon1, lat2, lon2):
    """Distancia aprox. entre dos puntos (Haversine)."""
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    a = sin(radians(lat2-lat1)/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(radians(lon2-lon1)/2)**2
    return round(R * 2 * atan2(sqrt(a), sqrt(1-a)), 1)

if __name__ == "__main__":
    pos = posicion_actual()
    dist = distancia_km(LAT, LON, pos["lat"], pos["lon"])
    print(f"\nISS ahora mismo:")
    print(f" Posición: {pos['lat']}, {pos['lon']}")
    print(f" Altitud: {pos['altitud']} km")
    print(f" Velocidad: {pos['velocidad']} km/h")
    print(f" Distancia desde {CITY}: {dist} km")
    print(f" Hora UTC: {pos['timestamp'].strftime('%H:%M:%S')}")