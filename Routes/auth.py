from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from DataBase.models.administrador import Administrador
from DataBase.models.database import db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Autenticación de administradores"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Usuario y contraseña requeridos'}), 400

        # Buscar administrador activo
        admin = Administrador.query.filter_by(username=username, activo=True).first()

        if admin and admin.check_password(password):
            # Actualizar último acceso
            admin.ultimo_acceso = datetime.utcnow()
            db.session.commit()

            # Crear token JWT
            access_token = create_access_token(identity=admin.id)

            return jsonify({
                'success': True,
                'token': access_token,
                'user': {
                    'id': admin.id,
                    'username': admin.username,
                    'nombre_completo': admin.nombre_completo,
                    'rol': admin.rol,
                    'email': admin.email
                }
            })

        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

    except Exception as e:
        return jsonify({'success': False, 'error': f'Error en autenticación: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtener información del usuario actual"""
    try:
        current_user_id = get_jwt_identity()
        admin = Administrador.query.get(current_user_id)

        if not admin or not admin.activo:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

        return jsonify({
            'success': True,
            'user': {
                'id': admin.id,
                'username': admin.username,
                'nombre_completo': admin.nombre_completo,
                'rol': admin.rol,
                'email': admin.email,
                'ultimo_acceso': admin.ultimo_acceso.isoformat() if admin.ultimo_acceso else None
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Cambiar contraseña del usuario actual"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return jsonify({'success': False, 'error': 'Contraseña actual y nueva contraseña requeridas'}), 400

        admin = Administrador.query.get(current_user_id)

        if not admin.check_password(current_password):
            return jsonify({'success': False, 'error': 'Contraseña actual incorrecta'}), 400

        admin.set_password(new_password)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

