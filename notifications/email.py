"""Envío de correos con SendGrid y plantillas HTML de las alertas."""
import logging
from html import escape

from config import SENDGRID_API_KEY, EMAIL_FROM, CITY

log = logging.getLogger(__name__)

ESTILO_CAJA = "background:#0B0718;color:#ECE8F5;padding:24px;font-family:sans-serif;border-radius:12px;"
CABECERA    = '<h2 style="color:#BA55D3;letter-spacing:2px;">⬡ ASTROALERT</h2>'


def correo_configurado():
    return bool(SENDGRID_API_KEY and EMAIL_FROM)


def enviar_alerta(destinatario, asunto, cuerpo_html):
    if not correo_configurado():
        log.warning("SendGrid no configurado: no se envía '%s' a %s", asunto, destinatario)
        return False
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    try:
        SendGridAPIClient(SENDGRID_API_KEY).send(Mail(
            from_email=EMAIL_FROM, to_emails=destinatario, subject=asunto, html_content=cuerpo_html))
        log.info("Correo enviado a %s: %s", destinatario, asunto)
        return True
    except Exception:
        log.exception("Error enviando correo a %s", destinatario)
        return False


def _pie():
    return (f'<hr style="border-color:#2C1E5C;margin:16px 0;">'
            f'<p style="font-size:12px;color:#9370DB;">AstroAlert · {escape(CITY)}. '
            f'Recibes este correo porque activaste las alertas; puedes desactivarlas desde la app.</p>')


def html_iss(distancia, lat, lon, velocidad):
    return f"""
    <div style="{ESTILO_CAJA}">
      {CABECERA}
      <h3 style="margin-top:16px;">🛰️ La ISS está pasando cerca de {escape(CITY)}</h3>
      <p style="color:#B8B0CC;">La Estación Espacial Internacional se encuentra a:</p>
      <p style="font-size:28px;font-weight:700;color:#BA55D3;">{distancia:,.0f} km</p>
      <p style="color:#B8B0CC;">Posición: {lat}, {lon} · Velocidad: {velocidad:,.0f} km/h</p>
      <p style="color:#B8B0CC;">Ya es de noche: si el cielo está despejado, busca un punto brillante que cruza sin parpadear.</p>
      {_pie()}
    </div>"""


def html_resumen(planetas, hora, eventos):
    if planetas:
        lista = ''.join(
            f"<li style='margin:6px 0;'><strong style='color:#BA55D3'>{escape(p['planeta'])}</strong> — "
            f"{p['altitud']}° de altura hacia el {p['direccion']}</li>" for p in planetas)
        bloque = f"<h3>🪐 Esta noche desde las {hora}</h3><ul>{lista}</ul>"
    else:
        bloque = "<h3>🪐 Esta noche</h3><p style='color:#B8B0CC;'>No hay planetas visibles en las primeras horas de la noche.</p>"
    if eventos:
        bloque += "<h3>📅 Próximas 48 horas</h3><ul>" + ''.join(
            f"<li style='margin:6px 0;'>{escape(e)}</li>" for e in eventos) + "</ul>"
    return f"""
    <div style="{ESTILO_CAJA}">
      {CABECERA}
      {bloque}
      {_pie()}
    </div>"""
