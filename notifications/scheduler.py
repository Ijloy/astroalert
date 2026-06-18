from apscheduler.schedulers.background import BackgroundScheduler
from events.iss import posicion_actual, distancia_km
from events.sky import planetas_visibles, proxima_ventana
from notifications.email import enviar_alerta, html_iss, html_planeta
from database.models import db, Usuario
from config import LAT, LON
from flask import current_app

DISTANCIA_ALERTA_KM = 10000

def revisar_iss(app):
    with app.app_context():
        try:
            pos  = posicion_actual()
            dist = distancia_km(LAT, LON, pos['lat'], pos['lon'])

            if dist < DISTANCIA_ALERTA_KM:
                usuarios = Usuario.query.all()
                for u in usuarios:
                    enviar_alerta(
                        destinatario=u.email,
                        asunto=f"🛸 La ISS está a {dist:,.0f} km de Quito",
                        cuerpo_html=html_iss(dist, pos['lat'], pos['lon'], pos['velocidad'])
                    )
                print(f"ISS a {dist} km — alertas enviadas")
            else:
                print(f"ISS a {dist} km — sin alerta")
        except Exception as e:
            print(f"Error en revisar_iss: {e}")

def revisar_planetas(app):
    with app.app_context():
        try:
            ahora   = planetas_visibles()
            ventana = proxima_ventana() if not ahora else None

            if ahora:
                usuarios = Usuario.query.all()
                for u in usuarios:
                    enviar_alerta(
                        destinatario=u.email,
                        asunto="🪐 Planetas visibles ahora desde Quito",
                        cuerpo_html=html_planeta(ahora)
                    )
                print(f"{len(ahora)} planeta(s) visible(s) — alertas enviadas")
            elif ventana and ventana['en_horas'] == 1:
                usuarios = Usuario.query.all()
                for u in usuarios:
                    enviar_alerta(
                        destinatario=u.email,
                        asunto=f"🪐 En 1 hora podrás ver {ventana['planetas'][0]['planeta']}",
                        cuerpo_html=html_planeta([], proxima_hora=ventana['hora_local'])
                    )
        except Exception as e:
            print(f"Error en revisar_planetas: {e}")

def iniciar_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(revisar_iss,      'interval', minutes=5,  args=[app])
    scheduler.add_job(revisar_planetas, 'interval', minutes=30, args=[app])
    scheduler.start()
    print("Scheduler iniciado — revisando ISS cada 5min, planetas cada 30min")
    return scheduler