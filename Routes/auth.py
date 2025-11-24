from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from DataBase.models.administrador import Administrador
from DataBase.models.database import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login de administrador.
    Acepta JSON o form-data con:
    {
        "email": "admin@parnet.com",
        "password": "loquesea"
    }
    """
    try:
        # Aceptar JSON o form
        data = request.get_json(silent=True) or request.form

        if not data:
            return jsonify({
                "success": False,
                "error": "Datos no recibidos"
            }), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "success": False,
                "error": "Usuario y contraseña requeridos"
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
            # Si tu modelo ya tiene este método
            password_ok = admin.check_password(password)
        else:
            # Fallback: por si guardaste la contraseña en texto plano (no recomendado)
            # Ajusta a admin.password_hash si tu campo se llama así
            if hasattr(admin, "password"):
                password_ok = (admin.password == password)

        if not password_ok:
            return jsonify({
                "success": False,
                "error": "Credenciales incorrectas"
            }), 401

        # Crear token JWT
        access_token = create_access_token(identity=admin.id)

        # Asegurarnos de que existe to_dict()
        if hasattr(admin, "to_dict"):
            admin_data = admin.to_dict()
        else:
            admin_data = {
                "id": admin.id,
                "nombre": getattr(admin, "nombre", ""),
                "email": admin.email,
                "activo": getattr(admin, "activo", True)
            }

        return jsonify({
            "success": True,
            "access_token": access_token,
            "admin": admin_data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error en autenticación: {str(e)}"
        }), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Devuelve la info básica del admin autenticado.
    """
    try:
        admin_id = get_jwt_identity()
        admin = Administrador.query.get(admin_id)

        if not admin:
            return jsonify({
                "success": False,
                "error": "Administrador no encontrado"
            }), 404

        if hasattr(admin, "to_dict"):
            admin_data = admin.to_dict()
        else:
            admin_data = {
                "id": admin.id,
                "nombre": getattr(admin, "nombre", ""),
                "email": admin.email,
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
