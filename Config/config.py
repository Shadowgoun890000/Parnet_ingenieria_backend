import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración para Parnet Ingeniería"""

    # Configuración MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'parnet_ingenieria')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

    # URI de conexión MySQL
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-parnet-2024')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secreto-parnet-2024')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # File Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    # Agrega esto en la clase Config:
    CORS_ORIGINS = [
        'http://localhost:5000',  # Mismo puerto del backend
        'http://127.0.0.1:5000',
        'http://localhost:3000',  # Por si usas otro puerto
        'http://127.0.0.1:3000'
    ]

    # Debug
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'


# Crear instancia de configuración
config = Config()

# Crear directorio de uploads si no existe
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)