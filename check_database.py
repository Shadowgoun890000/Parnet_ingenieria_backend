import mysql.connector
from Config.config import config


def check_database_status():
    """Verificar estado completo de la base de datos"""
    try:
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            port=config.MYSQL_PORT
        )

        cursor = conn.cursor()

        print("🔍 Verificando estado de la base de datos...")
        print("=" * 50)

        # 1. Verificar tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print("📋 Tablas en la base de datos:")
        table_counts = {}

        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            table_counts[table_name] = count
            status = "✅" if count > 0 else "⚠️ "
            print(f"   {status} {table_name}: {count} registros")

        # 2. Verificar datos críticos
        print("\n📊 Verificación de datos críticos:")

        # Administradores
        cursor.execute("SELECT COUNT(*) FROM administradores WHERE activo = 1")
        admin_count = cursor.fetchone()[0]
        print(f"   👥 Administradores activos: {admin_count}")

        # Productos disponibles
        cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1 AND estatus = 'disponible'")
        productos_disponibles = cursor.fetchone()[0]
        print(f"   📦 Productos disponibles: {productos_disponibles}")

        # Servicios activos
        cursor.execute("SELECT COUNT(*) FROM servicios WHERE activo = 1")
        servicios_activos = cursor.fetchone()[0]
        print(f"   🔧 Servicios activos: {servicios_activos}")

        # Clientes activos
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
        clientes_activos = cursor.fetchone()[0]
        print(f"   🏢 Clientes activos: {clientes_activos}")

        # 3. Verificar relaciones
        print("\n🔗 Verificación de relaciones:")

        # Productos sin categoría
        cursor.execute("SELECT COUNT(*) FROM productos WHERE categoria_id IS NULL")
        productos_sin_categoria = cursor.fetchone()[0]
        status = "✅" if productos_sin_categoria == 0 else "❌"
        print(f"   {status} Productos sin categoría: {productos_sin_categoria}")

        # Solicitudes sin servicio
        cursor.execute("SELECT COUNT(*) FROM solicitudes_servicios WHERE servicio_id IS NULL")
        solicitudes_sin_servicio = cursor.fetchone()[0]
        status = "✅" if solicitudes_sin_servicio == 0 else "❌"
        print(f"   {status} Solicitudes sin servicio: {solicitudes_sin_servicio}")

        cursor.close()
        conn.close()

        # Resumen
        print("\n" + "=" * 50)
        total_tablas = len(tables)
        total_registros = sum(table_counts.values())

        print(f"📈 RESUMEN:")
        print(f"   • Tablas creadas: {total_tablas}")
        print(f"   • Registros totales: {total_registros}")

        if admin_count > 0 and productos_disponibles > 0 and servicios_activos > 0:
            print("🎉 ¡Base de datos configurada correctamente!")
            return True
        else:
            print("⚠️  La base de datos necesita atención")
            return False

    except mysql.connector.Error as e:
        print(f"❌ Error de MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


if __name__ == '__main__':
    check_database_status()