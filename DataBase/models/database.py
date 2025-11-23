from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Inicializar la base de datos con la aplicación Flask"""
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Importar modelos aquí para evitar circular imports
        try:
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
            print(f"✅ Base de datos: {app.config['MYSQL_DATABASE']}")
        except Exception as e:
            print(f"❌ Error inicializando base de datos: {e}")