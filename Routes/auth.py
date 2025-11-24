from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from DataBase.models.administrador import Administrador
from DataBase.models.database import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login de administrador.
    Acepta JSON con:
    {
        "email": "admin@parnet.com",
        "password": "password"
    }
    """
    try:
        # Solo aceptar JSON
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Datos JSON requeridos"
            }), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "success": False,
                "error": "Email y contraseña requeridos"
            }), 400

        # Buscar administrador activo
        admin = Administrador.query.filter_by(email=email, activo=True).first()

        if not admin:
            return jsonify({
                "success": False,
                "error": "Credenciales incorrectas"
            }), 401

        # Verificar contraseña
        password_ok = False
        if hasattr(admin, "check_password"):
            password_ok = admin.check_password(password)
        elif hasattr(admin, "password_hash"):
            # Si usas password hasheada
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            password_ok = (admin.password_hash == password_hash)
        elif hasattr(admin, "password"):
            # Fallback: texto plano (no recomendado para producción)
            password_ok = (admin.password == password)

        if not password_ok:
            return jsonify({
                "success": False,
                "error": "Credenciales incorrectas"
            }), 401

        # Crear token JWT
        access_token = create_access_token(identity=admin.id)

        # Datos del admin para el frontend
        admin_data = {
            "id": admin.id,
            "nombre": getattr(admin, "nombre", "Administrador"),
            "email": admin.email,
            "rol": getattr(admin, "rol", "admin"),
            "activo": getattr(admin, "activo", True)
        }

        return jsonify({
            "success": True,
            "access_token": access_token,
            "admin": admin_data,
            "message": "Login exitoso"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error en autenticación: {str(e)}"
        }), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Obtener información del admin autenticado"""
    try:
        admin_id = get_jwt_identity()
        admin = Administrador.query.get(admin_id)

        if not admin or not getattr(admin, "activo", True):
            return jsonify({
                "success": False,
                "error": "Administrador no encontrado"
            }), 404

        admin_data = {
            "id": admin.id,
            "nombre": getattr(admin, "nombre", "Administrador"),
            "email": admin.email,
            "rol": getattr(admin, "rol", "admin"),
            "activo": getattr(admin, "activo", True)
        }

        return jsonify({
            "success": True,
            "admin": admin_data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout del administrador"""
    try:
        # En JWT, el logout es manejado por el frontend eliminando el token
        return jsonify({
            "success": True,
            "message": "Logout exitoso"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@auth_bp.route("/check", methods=["GET"])
@jwt_required()
def check_token():
    """Verificar si el token JWT es válido"""
    try:
        admin_id = get_jwt_identity()
        admin = Administrador.query.get(admin_id)

        if not admin or not getattr(admin, "activo", True):
            return jsonify({
                "success": False,
                "error": "Token inválido"
            }), 401

        return jsonify({
            "success": True,
            "valid": True,
            "message": "Token válido"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500