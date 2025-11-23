from datetime import datetime

from flask import Flask, jsonify, request, send_file
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from Config.config import config
from DataBase.models.database import init_db, db
from Routes.auth import auth_bp
from Routes.productos import productos_bp
from Routes.servicios import servicios_bp
from Routes.dashboard import dashboard_bp
from Routes.contactos import contactos_bp
from Routes.public import public_bp

# Importar utilidades
from Utils.email_sender import email_sender
from Utils.singleton import stats_manager
from Utils.pdf_generator import PDFGenerator

# Inicializar extensiones
jwt = JWTManager()
mail = Mail()


def create_app(config_class=config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configurar extensiones
    init_db(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app, origins=config.CORS_ORIGINS)

    # Inicializar EmailSender
    email_sender.init_app(app)

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(productos_bp, url_prefix='/api/productos')
    app.register_blueprint(servicios_bp, url_prefix='/api/servicios')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(contactos_bp, url_prefix='/api/contactos')
    app.register_blueprint(public_bp, url_prefix='/api/public')

    # Middleware para estadísticas
    @app.before_request
    def track_visit():
        """Registrar visita para estadísticas"""
        if request.endpoint and 'static' not in request.endpoint:
            # Generar ID de sesión único
            session_id = request.headers.get('X-Session-ID')
            if not session_id:
                # Usar IP + User-Agent como fallback
                session_id = f"{request.remote_addr}-{hash(request.user_agent.string)}"

            stats_manager.register_visit(
                session_id=session_id,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                page=request.path
            )

    # =============================================
    # RUTAS DE UTILIDADES
    # =============================================

    @app.route('/')
    def home():
        return jsonify({
            'message': 'Bienvenido a Parnet Ingeniería API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'productos': '/api/productos',
                'servicios': '/api/servicios',
                'dashboard': '/api/dashboard',
                'public': '/api/public',
                'Utils': '/api/Utils'
            }
        })

    # Ruta para estadísticas del sitio
    @app.route('/api/stats')
    def get_site_stats():
        """Obtener estadísticas del sitio"""
        try:
            stats = stats_manager.get_stats()
            return jsonify({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Ruta para limpiar sesiones antiguas
    @app.route('/api/stats/cleanup', methods=['POST'])
    def cleanup_sessions():
        """Limpiar sesiones antiguas"""
        try:
            cleaned = stats_manager.cleanup_old_sessions(hours=1)
            return jsonify({
                'success': True,
                'message': f'Se limpiaron {cleaned} sesiones expiradas',
                'cleaned_count': cleaned
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Ruta para probar email
    @app.route('/api/utils/test-email', methods=['POST'])
    def test_email():
        """Enviar email de prueba"""
        try:
            data = request.get_json() or {}
            to_email = data.get('email')

            success = email_sender.send_test_email(to_email)
            return jsonify({
                'success': success,
                'message': 'Email de prueba enviado' if success else 'Error enviando email'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Ruta para generar PDF de producto
    @app.route('/api/utils/productos/<int:producto_id>/ficha-pdf', methods=['GET'])
    def generar_ficha_producto_pdf(producto_id):
        """Generar ficha técnica de producto en PDF"""
        try:
            from DataBase.models.producto import Producto
            producto = Producto.query.get_or_404(producto_id)

            # Generar PDF
            pdf = PDFGenerator.generate_product_sheet(producto)

            # Guardar temporalmente y enviar
            filename = f"ficha_tecnica_{producto.sku}_{producto.id}.pdf"
            filepath = PDFGenerator.save_pdf_to_file(pdf, filename)

            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Ruta para generar reporte de productos
    @app.route('/api/utils/productos/reporte-pdf', methods=['GET'])
    def generar_reporte_productos_pdf():
        """Generar reporte de productos en PDF"""
        try:
            from DataBase.models.producto import Producto
            from flask_jwt_extended import jwt_required

            # Solo administradores
            productos = Producto.query.filter_by(activo=True).all()

            # Generar PDF
            pdf = PDFGenerator.generate_products_report(productos)

            # Guardar temporalmente y enviar
            filename = f"reporte_productos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            filepath = PDFGenerator.save_pdf_to_file(pdf, filename)

            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Ruta para generar reporte de sugerencias
    @app.route('/api/utils/sugerencias/reporte-pdf', methods=['GET'])
    def generar_reporte_sugerencias_pdf():
        """Generar reporte de sugerencias en PDF"""
        try:
            from DataBase.models.contacto import Sugerencia
            from flask_jwt_extended import jwt_required

            # Solo administradores
            sugerencias = Sugerencia.query.all()

            # Generar PDF
            pdf = PDFGenerator.generate_suggestions_report(sugerencias)

            # Guardar temporalmente y enviar
            filename = f"reporte_sugerencias_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            filepath = PDFGenerator.save_pdf_to_file(pdf, filename)

            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Ruta de información de configuración
    @app.route('/api/utils/config-info')
    def get_config_info():
        """Obtener información de configuración (sin datos sensibles)"""
        try:
            config_info = {
                'database': {
                    'host': config.MYSQL_HOST,
                    'database': config.MYSQL_DATABASE,
                    'port': config.MYSQL_PORT
                },
                'mail': {
                    'server': config.MAIL_SERVER,
                    'port': config.MAIL_PORT,
                    'username_set': bool(config.MAIL_USERNAME)
                },
                'debug': config.DEBUG
            }

            return jsonify({
                'success': True,
                'config': config_info
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

    return app


# Crear aplicación
app = create_app()

if __name__ == '__main__':
    print("🚀 Iniciando Parnet Ingeniería API con utilidades...")
    print("📧 Email configurado:", "✅" if config.MAIL_USERNAME else "❌")
    print("📊 Estadísticas: ✅")
    print("📄 Generador PDF: ✅")

    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)