from dotenv import load_dotenv
import os

load_dotenv()

LAT  = float(os.getenv("LAT",  "-0.18"))   # Quito está ~0.18° al SUR del ecuador
LON  = float(os.getenv("LON",  "-78.47"))
ALT  = float(os.getenv("ALT",  "2850"))
CITY = os.getenv("CITY", "Quito")
TZ_NAME = os.getenv("TZ_NAME", "America/Guayaquil")

SECRET_KEY     = os.getenv("SECRET_KEY",     "dev-secret")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
DATABASE_URL   = "sqlite:///astroalert.db"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
EMAIL_FROM       = os.getenv("EMAIL_FROM", "")
