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
                static_folder='static',  # Carpeta para archivos estáticos
                template_folder='templates')  # Carpeta para templates
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
    def index():
        """Servir página principal"""
        return render_template('index.html')

    @app.route('/admin')
    def admin():
        """Página de administración"""
        return render_template('admin.html')

    @app.route('/contacto')
    def contacto():
        """Página de contacto"""
        return render_template('contacto.html')

    @app.route('/noticias')
    def noticias():
        """Página de noticias"""
        return render_template('noticias.html')

    @app.route('/productos')
    def productos():
        """Página de productos"""
        return render_template('productos.html')

    @app.route('/servicios')
    def servicios():
        """Página de servicios"""
        return render_template('servicios.html')

    @app.route('/quienes_somos')
    def quienes_somos():
        """Página quiénes somos"""
        # Si no existe el template, servir uno básico
        try:
            return render_template('quienes_somos.html')
        except:
            return render_template('index.html')

    @app.route('/clientes')
    def clientes():
        """Página de clientes"""
        try:
            return render_template('clientes.html')
        except:
            return render_template('index.html')

    @app.route('/casos_exito')
    def casos_exito():
        """Página de casos de éxito"""
        try:
            return render_template('casos_exito.html')
        except:
            return render_template('index.html')

    @app.route('/socios')
    def socios():
        """Página de socios"""
        try:
            return render_template('socios.html')
        except:
            return render_template('index.html')

    @app.route('/soporte')
    def soporte():
        """Página de soporte"""
        try:
            return render_template('soporte.html')
        except:
            return render_template('index.html')

    # Ruta para servir archivos estáticos
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)

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
                'contactos': '/api/contactos',
                'utils': '/api/utils'
            },
            'frontend_routes': {
                'inicio': '/',
                'admin': '/admin',
                'contacto': '/contacto',
                'noticias': '/noticias',
                'productos': '/productos',
                'servicios': '/servicios',
                'quienes_somos': '/quienes_somos',
                'clientes': '/clientes',
                'casos_exito': '/casos_exito',
                'socios': '/socios',
                'soporte': '/soporte'
            }
        })

    @app.route('/api/stats')
    def get_site_stats():
        """Obtener estadísticas del sitio"""
        try:
            stats = stats_manager.get_stats()
            return jsonify({'success': True, 'stats': stats})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/stats/cleanup', methods=['POST'])
    def cleanup_sessions():
        """Limpiar sesiones expiradas"""
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
        """Probar envío de email"""
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
        """Generar ficha técnica de producto en PDF"""
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
        """Generar reporte de productos en PDF"""
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
        """Generar reporte de sugerencias en PDF"""
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
        """Obtener información de configuración"""
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

    # ==================== MANEJO DE ERRORES ====================

    @app.errorhandler(404)
    def not_found(error):
        """Manejar errores 404"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Recurso API no encontrado'}), 404
        # Para rutas no-API, servir página 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Manejar errores 500"""
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Error interno del servidor'}), 500
        return render_template('500.html'), 500

    return app


app = create_app()

if __name__ == '__main__':
    print("🚀 Iniciando Parnet Ingeniería - Sistema Completo")
    print("✅ Base de datos inicializada correctamente")
    print(f"✅ Base de datos: {config.MYSQL_DATABASE}")
    print("📧 Email configurado:", "✔️" if config.MAIL_USERNAME else "❌")
    print("📊 Estadísticas activas ✔️")
    print("📄 Generador PDF listo ✔️")
    print("🌐 Frontend disponible en: http://localhost:5000")
    print("🔌 API disponible en: http://localhost:5000/api")

    # Verificar estructura de carpetas
    templates_path = 'templates'
    static_path = 'static'

    if os.path.exists(templates_path):
        templates = [f for f in os.listdir(templates_path) if f.endswith('.html')]
        print(f"📁 Templates cargados: {len(templates)}")
        for template in templates:
            print(f"   📄 {template}")
    else:
        print("❌ Carpeta 'templates' no encontrada")

    if os.path.exists(static_path):
        static_folders = [f for f in os.listdir(static_path) if os.path.isdir(os.path.join(static_path, f))]
        print(f"📁 Carpetas estáticas: {', '.join(static_folders)}")
    else:
        print("❌ Carpeta 'static' no encontrada")

    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)