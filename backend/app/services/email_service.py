"""
Servicio de envío de correos usando smtplib (sin dependencias extra).
Configurar en .env:
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=tu_correo@gmail.com
  SMTP_PASSWORD=tu_app_password
  SMTP_FROM=tu_correo@gmail.com   (opcional, por defecto usa SMTP_USER)

Para Gmail: activar "Contraseñas de aplicación" en la cuenta de Google.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from app.config           import settings


def enviar_otp_reset(destinatario: str, nombre: str, otp: str) -> None:
    """Envía el código OTP de restablecimiento de contraseña."""

    asunto = "Código de verificación — Sistema de Horarios CTP Heredia"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"/></head>
    <body style="margin:0;padding:0;background:#f3f4f6;font-family:system-ui,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td align="center" style="padding:40px 16px;">
          <table width="480" cellpadding="0" cellspacing="0"
                 style="background:white;border-radius:16px;overflow:hidden;
                        box-shadow:0 4px 24px rgba(0,0,0,0.08);">

            <!-- Encabezado verde -->
            <tr>
              <td style="background:linear-gradient(135deg,#166534,#15803d);
                         padding:32px 40px;text-align:center;">
                <div style="font-size:36px;margin-bottom:8px;">📅</div>
                <h1 style="color:white;margin:0;font-size:22px;font-weight:700;">
                  CTP Heredia
                </h1>
                <p style="color:#bbf7d0;margin:4px 0 0;font-size:13px;">
                  Sistema de Gestión de Horarios
                </p>
              </td>
            </tr>

            <!-- Cuerpo -->
            <tr>
              <td style="padding:36px 40px;">
                <p style="color:#374151;font-size:15px;margin:0 0 8px;">
                  Hola, <strong>{nombre}</strong>
                </p>
                <p style="color:#6b7280;font-size:14px;margin:0 0 28px;">
                  Recibimos una solicitud para restablecer la contraseña de tu cuenta.
                  Usá el siguiente código de verificación:
                </p>

                <!-- OTP box -->
                <div style="background:#f0fdf4;border:2px dashed #4ade80;
                            border-radius:12px;padding:20px;text-align:center;
                            margin-bottom:28px;">
                  <span style="font-size:40px;font-weight:800;letter-spacing:10px;
                               color:#166534;font-family:monospace;">
                    {otp}
                  </span>
                  <p style="color:#6b7280;font-size:12px;margin:10px 0 0;">
                    Válido por <strong>15 minutos</strong> · Un solo uso
                  </p>
                </div>

                <p style="color:#9ca3af;font-size:12px;margin:0;
                          border-top:1px solid #e5e7eb;padding-top:20px;">
                  Si no solicitaste este código, ignorá este correo.
                  Tu contraseña no cambiará a menos que ingreses el código.
                </p>
              </td>
            </tr>

            <!-- Footer -->
            <tr>
              <td style="background:#f9fafb;padding:16px 40px;
                         border-top:1px solid #e5e7eb;text-align:center;">
                <p style="color:#d1d5db;font-size:11px;margin:0;">
                  Colegio Técnico Profesional de Heredia © 2025
                </p>
              </td>
            </tr>

          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

    smtp_from = settings.smtp_from or settings.smtp_user

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"]    = f"CTP Heredia <{smtp_from}>"
    msg["To"]      = destinatario
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(smtp_from, destinatario, msg.as_string())
