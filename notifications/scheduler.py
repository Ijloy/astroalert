"""Alertas por correo programadas.

Antes: cada 5 min se enviaba un correo a TODOS los usuarios si la ISS estaba a
menos de 10.000 km (casi siempre), y cada 30 min otro de planetas (que por el
error del Sol se disparaba también de día). Eso es spam y agota la cuota de
SendGrid. Ahora:

* Solo reciben correos los usuarios que activaron `recibir_alertas`.
* ISS: aviso si pasa a menos de ISS_ALERTA_KM y es de noche, como máximo una
  vez cada 12 h por usuario.
* Resumen diario: un correo por día a la HORA_RESUMEN local con los planetas
  de esa noche y los eventos de las próximas 48 h.
* El planificador solo arranca con ENABLE_SCHEDULER=true y un único proceso
  lo ejecuta (candado de archivo), así no se duplican correos con varios
  workers de gunicorn.
"""
import fcntl
import logging
import os
import tempfile
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from config import LAT, LON, ENABLE_SCHEDULER, ISS_ALERTA_KM, HORA_RESUMEN, TZ_NAME
from database.models import db, Usuario
from events.iss import posicion_actual, distancia_km
from events.sky import estado_cielo, proxima_ventana, planetas_visibles
from events.eclipses import proximos_eclipses
from events.conjunciones import proximas_conjunciones
from events.oposiciones import proximas_oposiciones
from notifications.email import enviar_alerta, html_iss, html_resumen, correo_configurado

log = logging.getLogger(__name__)

PAUSA_ISS = timedelta(hours=12)
_candado  = None


def _suscritos():
    return Usuario.query.filter_by(recibir_alertas=True).all()


def revisar_iss(app):
    with app.app_context():
        try:
            if estado_cielo()['condicion'] != 'noche':
                return
            pos  = posicion_actual()
            dist = distancia_km(LAT, LON, pos['lat'], pos['lon'])
            if dist > ISS_ALERTA_KM:
                return
            ahora = datetime.now(timezone.utc)
            enviados = 0
            for u in _suscritos():
                ultima = u.ultima_alerta_iss
                if ultima and ultima.tzinfo is None:
                    ultima = ultima.replace(tzinfo=timezone.utc)
                if ultima and ahora - ultima < PAUSA_ISS:
                    continue
                if enviar_alerta(u.email, f"🛰️ La ISS pasa a {dist:,.0f} km de ti",
                                 html_iss(dist, pos['lat'], pos['lon'], pos['velocidad'])):
                    u.ultima_alerta_iss = ahora
                    enviados += 1
            db.session.commit()
            log.info("ISS a %.0f km: %d alertas enviadas", dist, enviados)
        except Exception:
            log.exception("Error en revisar_iss")


def _eventos_proximos(horas=48):
    limite = datetime.now(timezone.utc).timestamp() + horas * 3600
    textos = []
    for e in proximos_eclipses():
        if e['timestamp'] <= limite and e['visible_local']:
            textos.append(f"Eclipse {e['tipo'].lower()} ({e['fecha_local']}): {e['descripcion']}")
    for c in proximas_conjunciones():
        if c['timestamp'] <= limite and c['observable']:
            textos.append(f"Conjunción {c['planeta1']} y {c['planeta2']} a {c['separacion']}° ({c['fecha_local']})")
    for o in proximas_oposiciones():
        if o['timestamp'] <= limite:
            textos.append(f"Oposición de {o['planeta']} ({o['fecha_local']})")
    return textos


def enviar_resumen_diario(app):
    with app.app_context():
        try:
            hoy = datetime.now(timezone.utc).date()
            ventana  = proxima_ventana(horas=6) if not planetas_visibles() else None
            planetas = planetas_visibles() or (ventana['planetas'] if ventana else [])
            hora     = ventana['hora_local'] if ventana else 'el anochecer'
            eventos  = _eventos_proximos()
            cuerpo   = html_resumen(planetas, hora, eventos)
            enviados = 0
            for u in _suscritos():
                if u.ultimo_resumen_diario == hoy:
                    continue
                if enviar_alerta(u.email, "🔭 Tu cielo de esta noche", cuerpo):
                    u.ultimo_resumen_diario = hoy
                    enviados += 1
            db.session.commit()
            log.info("Resumen diario: %d correos enviados", enviados)
        except Exception:
            log.exception("Error en enviar_resumen_diario")


def _tomar_candado():
    """Solo el primer proceso que tome el candado ejecuta el planificador."""
    global _candado
    ruta = os.path.join(tempfile.gettempdir(), 'astroalert-scheduler.lock')
    _candado = open(ruta, 'w')
    try:
        fcntl.flock(_candado, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        _candado.close()
        _candado = None
        return False


def iniciar_scheduler(app):
    if not ENABLE_SCHEDULER:
        log.info("Planificador de alertas desactivado (ENABLE_SCHEDULER=false)")
        return None
    if not correo_configurado():
        log.warning("ENABLE_SCHEDULER=true pero SendGrid no está configurado: no se enviarán correos")
    if not _tomar_candado():
        log.info("Otro proceso ya ejecuta el planificador")
        return None

    hora, minuto = (int(x) for x in HORA_RESUMEN.split(':'))
    scheduler = BackgroundScheduler(timezone=TZ_NAME)
    scheduler.add_job(revisar_iss, 'interval', minutes=5, args=[app], id='iss')
    scheduler.add_job(enviar_resumen_diario, 'cron', hour=hora, minute=minuto, args=[app], id='resumen')
    scheduler.start()
    log.info("Planificador iniciado: ISS cada 5 min, resumen diario a las %s (%s)", HORA_RESUMEN, TZ_NAME)
    return scheduler
