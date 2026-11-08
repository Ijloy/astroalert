"""Configuración leída de variables de entorno (ver .env.example)."""
from dotenv import load_dotenv
import os

load_dotenv()


def _bool(nombre, defecto=False):
    return os.getenv(nombre, str(defecto)).strip().lower() in ('1', 'true', 'yes', 'si', 'sí')


APP_ENV       = os.getenv("APP_ENV", "development")       # development | production
EN_PRODUCCION = APP_ENV == "production"

# ── Ubicación del observador ──
LAT  = float(os.getenv("LAT",  "-0.18"))   # Quito está ~0.18° al SUR del ecuador
LON  = float(os.getenv("LON",  "-78.47"))
ALT  = float(os.getenv("ALT",  "2850"))
CITY = os.getenv("CITY", "Quito")
TZ_NAME = os.getenv("TZ_NAME", "America/Guayaquil")

# ── Secretos ──
SECRET_KEY     = os.getenv("SECRET_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if EN_PRODUCCION and (not SECRET_KEY or not JWT_SECRET_KEY):
    # Mejor no arrancar que arrancar con claves conocidas por todos.
    raise RuntimeError("En producción SECRET_KEY y JWT_SECRET_KEY son obligatorias.")
SECRET_KEY     = SECRET_KEY or "dev-secret-solo-local-no-usar-en-produccion"
JWT_SECRET_KEY = JWT_SECRET_KEY or "dev-jwt-secret-solo-local-no-usar-en-produccion"

# ── Base de datos ──
# En Render/Neon/Supabase llega como postgres://...; SQLAlchemy necesita postgresql://
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///astroalert.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── CORS ──
# La web y la API se sirven desde el mismo dominio, así que por defecto no se
# permite ningún origen externo. Para habilitar alguno: CORS_ORIGINS=https://a.com,https://b.com
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

# ── Alertas por correo ──
ENABLE_SCHEDULER = _bool("ENABLE_SCHEDULER", False)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
EMAIL_FROM       = os.getenv("EMAIL_FROM", "")
ISS_ALERTA_KM    = float(os.getenv("ISS_ALERTA_KM", "1500"))
HORA_RESUMEN     = os.getenv("HORA_RESUMEN", "17:30")       # hora local del resumen diario

# ── APIs externas ──
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

# ── Límite de peticiones (login/registro) ──
RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
