from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import SENDGRID_API_KEY, EMAIL_FROM

def enviar_alerta(destinatario, asunto, cuerpo_html):
    mensaje = Mail(
        from_email=EMAIL_FROM,
        to_emails=destinatario,
        subject=asunto,
        html_content=cuerpo_html
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(mensaje)
        print(f"Email enviado a {destinatario}")
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def html_iss(distancia, lat, lon, velocidad):
    return f"""
    <div style="background:#0B0718;color:#ECE8F5;padding:24px;font-family:sans-serif;border-radius:12px;">
      <h2 style="color:#BA55D3;letter-spacing:2px;">⬡ ASTROALERT</h2>
      <h3 style="margin-top:16px;">🛸 La ISS está cerca de Quito</h3>
      <p style="color:#B8B0CC;">La Estación Espacial Internacional se encuentra a:</p>
      <p style="font-size:28px;font-weight:700;color:#BA55D3;">{distancia:,} km</p>
      <p style="color:#B8B0CC;">Posición: {lat}, {lon}</p>
      <p style="color:#B8B0CC;">Velocidad: {velocidad:,} km/h</p>
      <hr style="border-color:#2C1E5C;margin:16px 0;">
      <p style="font-size:12px;color:#9370DB;">AstroAlert · Quito, Ecuador</p>
    </div>
    """

def html_planeta(planetas, proxima_hora=None):
    if planetas:
        lista = ''.join([
            f"<li style='margin:8px 0;'><strong style='color:#BA55D3'>{p['planeta']}</strong> "
            f"— {p['altitud']}° de altura hacia el {p['direccion']}</li>"
            for p in planetas
        ])
        cuerpo = f"<h3>🪐 Planetas visibles ahora desde Quito</h3><ul>{lista}</ul>"
    else:
        cuerpo = f"<h3>🪐 Próxima ventana planetaria</h3><p>A las <strong style='color:#BA55D3'>{proxima_hora}</strong> podrás ver planetas desde Quito.</p>"

    return f"""
    <div style="background:#0B0718;color:#ECE8F5;padding:24px;font-family:sans-serif;border-radius:12px;">
      <h2 style="color:#BA55D3;letter-spacing:2px;">⬡ ASTROALERT</h2>
      {cuerpo}
      <hr style="border-color:#2C1E5C;margin:16px 0;">
      <p style="font-size:12px;color:#9370DB;">AstroAlert · Quito, Ecuador</p>
    </div>
    """