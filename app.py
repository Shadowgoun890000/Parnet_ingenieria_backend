from datetime import datetime
from flask import Flask, jsonify, request, send_file, send_from_directory, render_template
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
from Utils.email_sender import email_sender
from Utils.singleton import stats_manager
from Utils.pdf_generator import PDFGenerator
import os

jwt = JWTManager()
mail = Mail()


def create_app(config_class=config):
    app = Flask(__name__,
                static_folder='.',  # Sirve archivos desde la raíz
                static_url_path='')
    app.config.from_object(config_class)

    init_db(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app, resources={
        r"/api/*": {"origins": config.CORS_ORIGINS}
    })
    email_sender.init_app(app)

    # Registrar blueprints de API
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(productos_bp, url_prefix='/api/productos')
    app.register_blueprint(servicios_bp, url_prefix='/api/servicios')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(contactos_bp, url_prefix='/api/contactos')
    app.register_blueprint(public_bp, url_prefix='/api/public')

    @app.before_request
    def track_visit():
        """Registrar visitante único para estadísticas"""
        if request.endpoint and 'static' not in request.endpoint and request.path.startswith('/api/'):
            session_id = request.headers.get('X-Session-ID')
            if not session_id:
                session_id = f"{request.remote_addr}-{hash(request.user_agent.string)}"
            stats_manager.register_visit(
                session_id=session_id,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                page=request.path
            )

    # ==================== RUTAS DEL FRONTEND ====================

    @app.route('/')
    def serve_index():
        """Servir página principal"""
        return send_file('index.html')

    @app.route('/<page_name>')
    def serve_pages(page_name):
        """Servir páginas HTML del frontend"""
        valid_pages = [
            'productos', 'servicios', 'noticias', 'contacto', 'admin',
            'quienes_somos', 'clientes', 'casos_exito', 'socios', 'soporte'
        ]
        if page_name in valid_pages and os.path.exists(f'{page_name}.html'):
            return send_file(f'{page_name}.html')
        else:
            return jsonify({'error': 'Página no encontrada'}), 404

    # ==================== RUTAS DE LA API ====================

    @app.route('/api')
    def api_home():
        """Endpoint raíz de la API"""
        return jsonify({
            'message': 'Bienvenido a Parnet Ingeniería API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'dashboard': '/api/dashboard',
                'productos': '/api/productos',
                'servicios': '/api/servicios',
                'public': '/api/public',
                'utils': '/api/utils'
            }
        })

    @app.route('/api/stats')
    def get_site_stats():
        try:
            stats = stats_manager.get_stats()
            return jsonify({'success': True, 'stats': stats})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ... (mantén el resto de tus rutas API igual)
    @app.route('/api/stats/cleanup', methods=['POST'])
    def cleanup_sessions():
        try:
            cleaned = stats_manager.cleanup_old_sessions(hours=1)
            return jsonify({
                'success': True,
                'message': f'Se limpiaron {cleaned} sesiones expiradas',
                'cleaned_count': cleaned
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/utils/test-email', methods=['POST'])
    def test_email():
        try:
            data = request.get_json() or {}
            to_email = data.get('email')
            success = email_sender.send_test_email(to_email)
            return jsonify({
                'success': success,
                'message': 'Email enviado correctamente' if success else 'Error al enviar email'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/utils/productos/<int:producto_id>/ficha-pdf', methods=['GET'])
    def generar_ficha_producto_pdf(producto_id):
        try:
            from DataBase.models.producto import Producto
            producto = Producto.query.get_or_404(producto_id)
            pdf = PDFGenerator.generate_product_sheet(producto)
            filename = f"ficha_tecnica_{producto.sku}_{producto.id}.pdf"
            filepath = PDFGenerator.save_pdf_to_file(pdf, filename)
            return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/pdf')
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/utils/productos/reporte-pdf', methods=['GET'])
    def generar_reporte_productos_pdf():
        try:
            from DataBase.models.producto import Producto
            productos = Producto.query.filter_by(activo=True).all()
            pdf = PDFGenerator.generate_products_report(productos)
            filename = f"reporte_productos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            filepath = PDFGenerator.save_pdf_to_file(pdf, filename)
            return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/pdf')
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/utils/sugerencias/reporte-pdf', methods=['GET'])
    def generar_reporte_sugerencias_pdf():
        try:
            from DataBase.models.contacto import Sugerencia
            sugerencias = Sugerencia.query.all()
            pdf = PDFGenerator.generate_suggestions_report(sugerencias)
            filename = f"reporte_sugerencias_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            filepath = PDFGenerator.save_pdf_to_file(pdf, filename)
            return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/pdf')
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/utils/config-info')
    def get_config_info():
        try:
            return jsonify({
                'success': True,
                'config': {
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
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Recurso API no encontrado'}), 404
        # Para rutas no-API, servir index.html (para SPA)
        return send_file('index.html')

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

    return app


app = create_app()

if __name__ == '__main__':
    print("🚀 Iniciando Parnet Ingeniería - Sistema Completo")
    print("📧 Email configurado:", "✔️" if config.MAIL_USERNAME else "❌")
    print("📊 Estadísticas activas ✔️")
    print("📄 Generador PDF listo ✔️")
    print("🌐 Frontend disponible en: http://localhost:5000")
    print("🔌 API disponible en: http://localhost:5000/api")

    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)