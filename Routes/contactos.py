from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from DataBase.models.contacto import Contacto, Sugerencia
from DataBase.models.database import db
from Utils.email_sender import email_sender
import datetime

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

        db.session.add(contacto)
        db.session.commit()

        # Enviar email de notificación
        try:
            email_sender.send_contact_email({
                'nombre': contacto.nombre,
                'email': contacto.email,
                'telefono': contacto.telefono,
                'asunto': contacto.asunto,
                'mensaje': contacto.mensaje
            })
        except Exception as email_error:
            print(f"❌ Error enviando email de contacto: {email_error}")

        return jsonify({
            'success': True,
            'message': 'Mensaje enviado correctamente',
            'contacto': {
                'id': contacto.id,
                'nombre': contacto.nombre,
                'email': contacto.email,
                'asunto': contacto.asunto
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@contactos_bp.route('/contactos', methods=['GET'])
@jwt_required()
def listar_contactos():
    """Listar todos los contactos (admin)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        contactos = Contacto.query.order_by(Contacto.fecha_creacion.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'success': True,
            'contactos': [contacto.to_dict() for contacto in contactos.items],
            'total': contactos.total,
            'pages': contactos.pages,
            'current_page': page
        })

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

        db.session.add(sugerencia)
        db.session.commit()

        # Enviar email de notificación
        try:
            email_sender.send_suggestion_email(sugerencia)
        except Exception as email_error:
            print(f"❌ Error enviando email de sugerencia: {email_error}")

        return jsonify({
            'success': True,
            'message': 'Sugerencia enviada correctamente',
            'sugerencia': {
                'id': sugerencia.id,
                'nombre': sugerencia.nombre,
                'email': sugerencia.email,
                'asunto': sugerencia.asunto
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@contactos_bp.route('/sugerencias', methods=['GET'])
@jwt_required()
def listar_sugerencias():
    """Listar todas las sugerencias (admin)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        sugerencias = Sugerencia.query.order_by(Sugerencia.fecha_creacion.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'success': True,
            'sugerencias': [sugerencia.to_dict() for sugerencia in sugerencias.items],
            'total': sugerencias.total,
            'pages': sugerencias.pages,
            'current_page': page
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@contactos_bp.route('/contactos/<int:contacto_id>', methods=['DELETE'])
@jwt_required()
def eliminar_contacto(contacto_id):
    """Eliminar contacto (admin)"""
    try:
        contacto = Contacto.query.get_or_404(contacto_id)
        db.session.delete(contacto)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Contacto eliminado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@contactos_bp.route('/sugerencias/<int:sugerencia_id>', methods=['DELETE'])
@jwt_required()
def eliminar_sugerencia(sugerencia_id):
    """Eliminar sugerencia (admin)"""
    try:
        sugerencia = Sugerencia.query.get_or_404(sugerencia_id)
        db.session.delete(sugerencia)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Sugerencia eliminada correctamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@contactos_bp.route('/estadisticas', methods=['GET'])
@jwt_required()
def estadisticas_contactos():
    """Estadísticas de contactos y sugerencias"""
    try:
        # Contactos de los últimos 30 días
        fecha_limite = datetime.datetime.utcnow() - datetime.timedelta(days=30)

        total_contactos = Contacto.query.count()
        contactos_30_dias = Contacto.query.filter(
            Contacto.fecha_creacion >= fecha_limite
        ).count()

        total_sugerencias = Sugerencia.query.count()
        sugerencias_30_dias = Sugerencia.query.filter(
            Sugerencia.fecha_creacion >= fecha_limite
        ).count()

        return jsonify({
            'success': True,
            'estadisticas': {
                'total_contactos': total_contactos,
                'contactos_30_dias': contactos_30_dias,
                'total_sugerencias': total_sugerencias,
                'sugerencias_30_dias': sugerencias_30_dias
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500