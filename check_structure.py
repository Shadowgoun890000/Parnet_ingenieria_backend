import os
import sys


def check_structure():
    """Verificar que toda la estructura de archivos esté en su lugar"""

    required_files = {
        'root': [
            'app.py', 'requirements.txt', 'run.py',
            'init_database.py', 'seed_database.py', 'check_database.py'
        ],
        'DataBase':{
        'models': [
            '__init__.py', 'database.py', 'administrador.py', 'producto.py',
            'servicio.py', 'cliente.py', 'contacto.py', 'noticia.py'
        ]},
        'Routes': [
            '__init__.py', 'auth.py', 'productos.py', 'servicios.py',
            'dashboard.py', 'contactos.py', 'public.py'
        ],
        'Config': [
            'config.py',
        ]
    }

    print("🔍 Verificando estructura de archivos...")

    all_good = True

    for folder, files in required_files.items():
        if folder == 'root':
            current_dir = '.'
        else:
            current_dir = folder

        for file in files:
            file_path = os.path.join(current_dir, file)
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                print(f"❌ FALTANTE: {file_path}")
                all_good = False

    if all_good:
        print("\n🎉 ¡Estructura de archivos completa!")
        return True
    else:
        print("\n⚠️  Faltan algunos archivos. Por favor, créalos antes de continuar.")
        return False


if __name__ == '__main__':
    check_structure()