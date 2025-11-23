import os
import sys

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from DataBase.models.administrador import Administrador


def crear_administrador_inicial():
    with app.app_context():
        # Verificar si ya existe algún administrador
        if Administrador.query.first():
            print("⚠️  Ya existen administradores en la base de datos")
            return

        # Crear administrador principal
        admin = Administrador(
            username="admin",
            email="admin@parnet.com",
            nombre_completo="Administrador Principal",
            rol="admin"
        )

        try:
            admin.set_password("admin123")  # Cambiar en producción!
            db.session.add(admin)
            db.session.commit()

            print("✅ Administrador principal creado exitosamente!")
            print(f"👤 Usuario: admin")
            print(f"📧 Email: admin@parnet.com")
            print(f"🔑 Contraseña: admin123")
            print("⚠️  IMPORTANTE: Cambia la contraseña después del primer acceso")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creando administrador: {e}")


if __name__ == "__main__":
    crear_administrador_inicial()