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
                    return True
                except Exception as e:
                    print(f"❌ Error enviando email: {e}")
                    return False

        # Obtener la aplicación actual
        app = current_app._get_current_object()

        # Ejecutar en hilo separado
        thr = threading.Thread(target=async_send, args=[app, msg])
        thr.start()
        return thr

    def send_contact_email(self, contact_data):
        """Enviar email de notificación por contacto"""
        try:
            subject = f"📧 Nuevo mensaje de contacto: {contact_data.get('asunto', 'Consulta general')}"

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
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 25px; border-radius: 0 0 8px 8px; }}
                    .info-card {{ background: white; padding: 20px; border-radius: 8px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .message-card {{ background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3498db; }}
                    .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }}
                    .field {{ margin-bottom: 10px; }}
                    .field-label {{ font-weight: bold; color: #2c3e50; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 PARNET INGENIERÍA</h1>
                        <h2>Nuevo Mensaje de Contacto</h2>
                    </div>

                    <div class="content">
                        <div class="info-card">
                            <h3>📋 Información del Contacto</h3>
                            <div class="field">
                                <span class="field-label">Nombre:</span> {contact_data['nombre']}
                            </div>
                            <div class="field">
                                <span class="field-label">Email:</span> {contact_data['email']}
                            </div>
                            <div class="field">
                                <span class="field-label">Teléfono:</span> {contact_data.get('telefono', 'No proporcionado')}
                            </div>
                            <div class="field">
                                <span class="field-label">Asunto:</span> {contact_data.get('asunto', 'Consulta general')}
                            </div>
                        </div>

                        <div class="message-card">
                            <h3>💬 Mensaje</h3>
                            <p>{contact_data['mensaje'].replace(chr(10), '<br>')}</p>
                        </div>

                        <div class="info-card">
                            <p><strong>📅 Fecha de envío:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                        </div>
                    </div>

                    <div class="footer">
                        <p>Este email fue generado automáticamente por el sistema de Parnet Ingeniería.</p>
                        <p>© 2025 Parnet Ingeniería S.A. de C.V. - Todos los derechos reservados</p>
                    </div>
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
            subject = f"🔧 Nueva solicitud de servicio: {service.nombre}"

            msg = Message(
                subject=subject,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[current_app.config['MAIL_USERNAME']],
                reply_to=service_request.email  # ✅ Campo correcto
            )

            msg.body = f"""
            PARNET INGENIERÍA - NUEVA SOLICITUD DE SERVICIO

            Se ha recibido una nueva solicitud de servicio:

            🔧 SERVICIO SOLICITADO:
            • Servicio: {service.nombre}
            • ID de Servicio: {service.id}

            👤 INFORMACIÓN DEL CLIENTE:
            • Nombre: {service_request.nombre_cliente}  # ✅ Corregido
            • Email: {service_request.email}  # ✅ Campo correcto
            • Teléfono: {service_request.telefono or 'No proporcionado'}  # ✅ Corregido
            • Empresa: {service_request.empresa or 'No proporcionada'}  # ✅ Campo correcto

            💬 DETALLE DE LA SOLICITUD:
            {service_request.mensaje}  # ✅ Corregido

            📅 INFORMACIÓN DE LA SOLICITUD:
            • Fecha de solicitud: {service_request.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
            • ID de solicitud: {service_request.id}
            • Estado: {service_request.estado}

            ---
            Este email fue generado automáticamente por el sistema de Parnet Ingeniería.
            """

            # Versión HTML
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 25px; border-radius: 0 0 8px 8px; }}
                    .card {{ background: white; padding: 20px; border-radius: 8px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .service-card {{ background: #e8f6f3; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #27ae60; }}
                    .client-card {{ background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3498db; }}
                    .detail-card {{ background: #fef9e7; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #f39c12; }}
                    .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }}
                    .field {{ margin-bottom: 8px; }}
                    .field-label {{ font-weight: bold; color: #2c3e50; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔧 PARNET INGENIERÍA</h1>
                        <h2>Nueva Solicitud de Servicio</h2>
                    </div>

                    <div class="content">
                        <div class="service-card">
                            <h3>🔧 Servicio Solicitado</h3>
                            <div class="field">
                                <span class="field-label">Servicio:</span> {service.nombre}
                            </div>
                            <div class="field">
                                <span class="field-label">ID de Servicio:</span> {service.id}
                            </div>
                        </div>

                        <div class="client-card">
                            <h3>👤 Información del Cliente</h3>
                            <div class="field">
                                <span class="field-label">Nombre:</span> {service_request.nombre_cliente}  <!-- ✅ Corregido -->
                            </div>
                            <div class="field">
                                <span class="field-label">Email:</span> {service_request.email}  <!-- ✅ Campo correcto -->
                            </div>
                            <div class="field">
                                <span class="field-label">Teléfono:</span> {service_request.telefono or 'No proporcionado'}  <!-- ✅ Corregido -->
                            </div>
                            <div class="field">
                                <span class="field-label">Empresa:</span> {service_request.empresa or 'No proporcionada'}  <!-- ✅ Campo correcto -->
                            </div>
                        </div>

                        <div class="detail-card">
                            <h3>💬 Detalle de la Solicitud</h3>
                            <p>{service_request.mensaje.replace(chr(10), '<br>')}</p>  <!-- ✅ Corregido -->
                        </div>

                        <div class="card">
                            <h3>📅 Información de la Solicitud</h3>
                            <div class="field">
                                <span class="field-label">Fecha de solicitud:</span> {service_request.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
                            </div>
                            <div class="field">
                                <span class="field-label">ID de solicitud:</span> {service_request.id}
                            </div>
                            <div class="field">
                                <span class="field-label">Estado:</span> <strong>{service_request.estado}</strong>
                            </div>
                        </div>
                    </div>

                    <div class="footer">
                        <p>Este email fue generado automáticamente por el sistema de Parnet Ingeniería.</p>
                        <p>© 2025 Parnet Ingeniería S.A. de C.V. - Todos los derechos reservados</p>
                    </div>
                </div>
            </body>
            </html>
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
            subject = f"💡 Nueva sugerencia: {suggestion.asunto or 'Sin asunto'}"

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

            # Versión HTML
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #9b59b6, #8e44ad); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 25px; border-radius: 0 0 8px 8px; }}
                    .card {{ background: white; padding: 20px; border-radius: 8px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .suggestion-card {{ background: #f4ecf7; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #9b59b6; }}
                    .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }}
                    .field {{ margin-bottom: 8px; }}
                    .field-label {{ font-weight: bold; color: #2c3e50; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>💡 PARNET INGENIERÍA</h1>
                        <h2>Nueva Sugerencia</h2>
                    </div>

                    <div class="content">
                        <div class="card">
                            <h3>👤 Información del Remitente</h3>
                            <div class="field">
                                <span class="field-label">Nombre:</span> {suggestion.nombre}
                            </div>
                            <div class="field">
                                <span class="field-label">Email:</span> {suggestion.email}
                            </div>
                            <div class="field">
                                <span class="field-label">Asunto:</span> {suggestion.asunto or 'Sin asunto'}
                            </div>
                        </div>

                        <div class="suggestion-card">
                            <h3>💬 Sugerencia</h3>
                            <p>{suggestion.mensaje.replace(chr(10), '<br>')}</p>
                        </div>

                        <div class="card">
                            <div class="field">
                                <span class="field-label">📅 Fecha de envío:</span> {suggestion.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
                            </div>
                        </div>
                    </div>

                    <div class="footer">
                        <p>Este email fue generado automáticamente por el sistema de Parnet Ingeniería.</p>
                        <p>© 2025 Parnet Ingeniería S.A. de C.V. - Todos los derechos reservados</p>
                    </div>
                </div>
            </body>
            </html>
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

            # Versión HTML
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 25px; border-radius: 0 0 8px 8px; text-align: center; }}
                    .success {{ color: #27ae60; font-size: 48px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 PARNET INGENIERÍA</h1>
                        <h2>Email de Prueba</h2>
                    </div>

                    <div class="content">
                        <div class="success">✅</div>
                        <h3>Configuración Correcta</h3>
                        <p>Este es un email de prueba para verificar la configuración del sistema de correo.</p>
                        <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>

                    <div class="footer">
                        <p>Sistema de notificaciones - Parnet Ingeniería</p>
                        <p>© 2025 Parnet Ingeniería S.A. de C.V. - Todos los derechos reservados</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Enviar de forma asíncrona
            self.send_async_email(msg)
            return True

        except Exception as e:
            print(f"❌ Error enviando email de prueba: {e}")
            return False


# Instancia global
email_sender = EmailSender()