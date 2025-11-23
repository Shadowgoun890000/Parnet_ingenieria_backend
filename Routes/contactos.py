from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from DataBase.models.contacto import Contacto, Sugerencia
from DataBase.models.database import db
from Utils.email_sender import email_sender
from Utils.pdf_generator import PDFGenerator
import tempfile
from datetime import datetime

contactos_bp = Blueprint('contactos', __name__)

# ==================== CONTACTOS ====================

@contactos_bp.route('/contactos', methods=['POST'])
def crear_contacto():
    """Crear nuevo contacto desde formulario público"""
    try:
        data = request.get_json()

        # Validaciones
        required_fields = ['nombre', 'email', 'mensaje']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400

        contacto = Contacto(
            nombre=data['nombre'],
            email=data['email'],
            telefono=data.get('telefono'),
            asunto=data.get('asunto', 'Consulta general'),
            mensaje=data['mensaje']
        )

        if contacto.save():
            # Enviar email de notificación
            email_sender.send_contact_email({
                'nombre': contacto.nombre,
                'email': contacto.email,
                'telefono': contacto.telefono,
                'asunto': contacto.asunto,
                'mensaje': contacto.mensaje
            })

            return jsonify({'success': True, 'contacto': contacto.to_dict()}), 201
        else:
            return jsonify({'success': False, 'error': 'Error guardando contacto'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SUGERENCIAS ====================

@contactos_bp.route('/sugerencias', methods=['POST'])
def crear_sugerencia():
    """Crear nueva sugerencia desde formulario público"""
    try:
        data = request.get_json()

        # Validaciones
        required_fields = ['nombre', 'email', 'mensaje']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400

        sugerencia = Sugerencia(
            nombre=data['nombre'],
            email=data['email'],
            asunto=data.get('asunto', 'Sugerencia'),
            mensaje=data['mensaje']
        )

        if sugerencia.save():
            # Enviar email de notificación
            email_sender.send_suggestion_email(sugerencia)

            return jsonify({'success': True, 'sugerencia': sugerencia.to_dict()}), 201
        else:
            return jsonify({'success': False, 'error': 'Error guardando sugerencia'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ... (el resto del código se mantiene igual, solo quita las referencias a captcha)