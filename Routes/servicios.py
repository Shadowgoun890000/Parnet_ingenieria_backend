from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from DataBase.models.servicio import Servicio, SolicitudServicio
from DataBase.models.database import db
from Utils.email_sender import email_sender

servicios_bp = Blueprint('servicios', __name__)

# ==================== SOLICITUDES DE SERVICIOS ====================

@servicios_bp.route('/solicitudes', methods=['POST'])
def crear_solicitud_servicio():
    """Crear nueva solicitud de servicio"""
    try:
        data = request.get_json() or {}

        # Validaciones
        required_fields = ['servicio_id', 'nombre_cliente', 'email', 'mensaje']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400

        # Verificar que el servicio existe
        servicio = Servicio.query.get(data['servicio_id'])
        if not servicio:
            return jsonify({'success': False, 'error': 'Servicio no encontrado'}), 404

        solicitud = SolicitudServicio(
            servicio_id=data['servicio_id'],
            nombre_cliente=data['nombre_cliente'],
            email=data['email'],
            telefono=data.get('telefono'),
            empresa=data.get('empresa'),
            mensaje=data['mensaje']
        )

        if solicitud.save():
            # Enviar email de notificación
            try:
                email_sender.send_service_request_email(solicitud, servicio)
            except Exception:
                # Si el correo falla, no tiramos toda la API
                pass

            return jsonify({'success': True, 'solicitud': solicitud.to_dict()}), 201
        else:
            return jsonify({'success': False, 'error': 'Error guardando solicitud'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
