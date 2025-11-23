import os
import sys
import mysql.connector
from Config.config import config


def check_mysql_connection():
    """Verificar conexión a MySQL"""
    try:
        print("🔌 Verificando conexión a MySQL...")
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            port=config.MYSQL_PORT
        )

        if conn.is_connected():
            print("✅ Conexión a MySQL exitosa")
            return conn
        else:
            print("❌ No se pudo conectar a MySQL")
            return None

    except mysql.connector.Error as e:
        print(f"❌ Error de MySQL: {e}")
        return None
    except Exception as e:
        print(f"❌ Error general: {e}")
        return None


def create_database(conn):
    """Crear la base de datos si no existe"""
    try:
        cursor = conn.cursor()

        # Crear base de datos si no existe
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Base de datos '{config.MYSQL_DATABASE}' creada/verificada")

        # Usar la base de datos
        cursor.execute(f"USE {config.MYSQL_DATABASE}")

        # Mostrar bases de datos existentes
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print("📊 Bases de datos disponibles:")
        for db in databases:
            print(f"   - {db[0]}")

        cursor.close()
        return True

    except mysql.connector.Error as e:
        print(f"❌ Error creando base de datos: {e}")
        return False


def setup_flask_migrations():
    """Configurar migraciones de Flask-Migrate"""
    try:
        # Establecer variable de entorno para Flask
        os.environ['FLASK_APP'] = 'app.py'

        print("\n🔄 Configurando migraciones de Flask...")

        # Inicializar migraciones (solo primera vez)
        if not os.path.exists('migrations'):
            result = os.system('flask db init')
            if result == 0:
                print("✅ Directorio de migraciones creado")
            else:
                print("❌ Error creando directorio de migraciones")
                return False
        else:
            print("✅ Directorio de migraciones ya existe")

        # Crear migración inicial
        print("🔄 Creando migración inicial...")
        result = os.system('flask db migrate -m "Migración inicial - Parnet Ingeniería"')
        if result == 0:
            print("✅ Migración creada exitosamente")
        else:
            print("❌ Error creando migración")
            return False

        # Aplicar migración
        print("🔄 Aplicando migración a la base de datos...")
        result = os.system('flask db upgrade')
        if result == 0:
            print("✅ Migración aplicada correctamente")
            return True
        else:
            print("❌ Error aplicando migración")
            return False

    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False


def verify_tables():
    """Verificar que las tablas se crearon correctamente"""
    try:
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            port=config.MYSQL_PORT
        )

        cursor = conn.cursor()

        # Obtener todas las tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print("\n📋 Tablas creadas en la base de datos:")
        expected_tables = [
            'administradores', 'categorias_productos', 'productos',
            'servicios', 'solicitudes_servicios', 'clientes',
            'contactos', 'sugerencias', 'noticias'
        ]

        created_tables = [table[0] for table in tables]

        for expected_table in expected_tables:
            if expected_table in created_tables:
                print(f"   ✅ {expected_table}")
            else:
                print(f"   ❌ {expected_table} - FALTANTE")

        cursor.close()
        conn.close()

        return len(created_tables) >= len(expected_tables)

    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 Iniciando configuración de base de datos Parnet Ingeniería...")
    print("=" * 60)

    # Paso 1: Verificar conexión MySQL
    conn = check_mysql_connection()
    if not conn:
        print("\n💥 No se puede continuar sin conexión a MySQL")
        return

    # Paso 2: Crear base de datos
    if not create_database(conn):
        print("\n💥 Error creando base de datos")
        conn.close()
        return

    conn.close()

    # Paso 3: Configurar migraciones Flask
    if not setup_flask_migrations():
        print("\n💥 Error en migraciones Flask")
        return

    # Paso 4: Verificar tablas creadas
    if not verify_tables():
        print("\n⚠️  Algunas tablas podrían faltar")
    else:
        print("\n✅ Todas las tablas principales creadas")

    print("\n🎉 Configuración de base de datos COMPLETADA!")
    print("\n📝 Próximos pasos:")
    print("   1. Ejecutar: python seed_database.py")
    print("   2. Ejecutar: python run.py")
    print("   3. Verificar en: http://localhost:5000")


if __name__ == '__main__':
    main()