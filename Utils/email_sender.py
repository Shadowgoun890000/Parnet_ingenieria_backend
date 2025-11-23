from flask_mail import Mail, Message
from flask import current_app
import threading
from datetime import datetime


class EmailSender:
    """Clase para gestionar el envío de emails asíncronos"""

    def __init__(self, app=None):
        self.mail = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Inicializar con la aplicación Flask"""
        self.mail = Mail(app)

    def send_async_email(self, msg):
        """Enviar email de forma asíncrona"""

        def async_send(app, message):
            with app.app_context():
                try:
                    self.mail.send(message)
                    print(f"✅ Email enviado exitosamente: {message.subject}")
                except Exception as e:
                    print(f"❌ Error enviando email: {e}")

        # Obtener la aplicación actual
        app = current_app._get_current_object()

        # Ejecutar en hilo separado
        thr = threading.Thread(target=async_send, args=[app, msg])
        thr.start()
        return thr

    def send_contact_email(self, contact_data):
        """Enviar email de notificación por contacto"""
        try:
            subject = f"Nuevo mensaje de contacto: {contact_data.get('asunto', 'Consulta general')}"

            msg = Message(
                subject=subject,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[current_app.config['MAIL_USERNAME']],  # Enviar a sí mismo
                reply_to=contact_data['email']
            )

            # Cuerpo del email
            msg.body = f"""
            PARNET INGENIERÍA - NUEVO MENSAJE DE CONTACTO

            Has recibido un nuevo mensaje a través del formulario de contacto:

            📋 INFORMACIÓN DEL CONTACTO:
            • Nombre: {contact_data['nombre']}
            • Email: {contact_data['email']}
            • Teléfono: {contact_data.get('telefono', 'No proporcionado')}
            • Asunto: {contact_data.get('asunto', 'Consulta general')}

            💬 MENSAJE:
            {contact_data['mensaje']}

            📅 Fecha de envío: {datetime.now().strftime('%d/%m/%Y %H:%M')}

            ---
            Este email fue generado automáticamente por el sistema de Parnet Ingeniería.
            """

            # Versión HTML
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .info {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 10px 0; }}
                    .message {{ background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                    .footer {{ background: #ecf0f1; padding: 15px; text-align: center; font-size: 12px; color: #7f8c8d; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>PARNET INGENIERÍA</h1>
                    <h2>Nuevo Mensaje de Contacto</h2>
                </div>

                <div class="content">
                    <div class="info">
                        <h3>📋 Información del Contacto</h3>
                        <p><strong>Nombre:</strong> {contact_data['nombre']}</p>
                        <p><strong>Email:</strong> {contact_data['email']}</p>
                        <p><strong>Teléfono:</strong> {contact_data.get('telefono', 'No proporcionado')}</p>
                        <p><strong>Asunto:</strong> {contact_data.get('asunto', 'Consulta general')}</p>
                    </div>

                    <div class="message">
                        <h3>💬 Mensaje</h3>
                        <p>{contact_data['mensaje'].replace(chr(10), '<br>')}</p>
                    </div>

                    <p><strong>📅 Fecha de envío:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>

                <div class="footer">
                    <p>Este email fue generado automáticamente por el sistema de Parnet Ingeniería.</p>
                </div>
            </body>
            </html>
            """

            # Enviar de forma asíncrona
            self.send_async_email(msg)
            return True

        except Exception as e:
            print(f"❌ Error preparando email de contacto: {e}")
            return False

    def send_service_request_email(self, service_request, service):
        """Enviar email de notificación por solicitud de servicio"""
        try:
            subject = f"Nueva solicitud de servicio: {service.nombre}"

            msg = Message(
                subject=subject,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[current_app.config['MAIL_USERNAME']],
                reply_to=service_request.email
            )

            msg.body = f"""
            PARNET INGENIERÍA - NUEVA SOLICITUD DE SERVICIO

            Se ha recibido una nueva solicitud de servicio:

            🔧 SERVICIO SOLICITADO:
            • Servicio: {service.nombre}
            • Área: {service.area}

            👤 INFORMACIÓN DEL CLIENTE:
            • Nombre: {service_request.nombre_cliente}
            • Email: {service_request.email}
            • Teléfono: {service_request.telefono or 'No proporcionado'}
            • Empresa: {service_request.empresa or 'No proporcionada'}

            💬 MENSAJE:
            {service_request.mensaje}

            📅 Fecha de solicitud: {service_request.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
            🆔 ID de solicitud: {service_request.id}

            ---
            Este email fue generado automáticamente por el sistema de Parnet Ingeniería.
            """

            # Enviar de forma asíncrona
            self.send_async_email(msg)
            return True

        except Exception as e:
            print(f"❌ Error preparando email de servicio: {e}")
            return False

    def send_suggestion_email(self, suggestion):
        """Enviar email de notificación por sugerencia"""
        try:
            subject = f"Nueva sugerencia: {suggestion.asunto or 'Sin asunto'}"

            msg = Message(
                subject=subject,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[current_app.config['MAIL_USERNAME']],
                reply_to=suggestion.email
            )

            msg.body = f"""
            PARNET INGENIERÍA - NUEVA SUGERENCIA

            Se ha recibido una nueva sugerencia:

            👤 INFORMACIÓN DEL REMITENTE:
            • Nombre: {suggestion.nombre}
            • Email: {suggestion.email}
            • Asunto: {suggestion.asunto or 'Sin asunto'}

            💬 SUGERENCIA:
            {suggestion.mensaje}

            📅 Fecha de envío: {suggestion.fecha_creacion.strftime('%d/%m/%Y %H:%M')}

            ---
            Este email fue generado automáticamente por el sistema de Parnet Ingeniería.
            """

            # Enviar de forma asíncrona
            self.send_async_email(msg)
            return True

        except Exception as e:
            print(f"❌ Error preparando email de sugerencia: {e}")
            return False

    def send_test_email(self, to_email=None):
        """Enviar email de prueba"""
        try:
            recipient = to_email or current_app.config['MAIL_USERNAME']

            msg = Message(
                subject="✅ Email de prueba - Parnet Ingeniería",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[recipient]
            )

            msg.body = f"""
            PARNET INGENIERÍA - EMAIL DE PRUEBA

            Este es un email de prueba para verificar la configuración del sistema de correo.

            ✅ Configuración correcta
            📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

            ---
            Sistema de notificaciones - Parnet Ingeniería
            """

            # Enviar de forma asíncrona
            self.send_async_email(msg)
            return True

        except Exception as e:
            print(f"❌ Error enviando email de prueba: {e}")
            return False


# Instancia global
email_sender = EmailSender()