from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from DataBase.models.servicio import Servicio, SolicitudServicio
from DataBase.models.database import db
from Utils.email_sender import email_sender

servicios_bp = Blueprint('servicios', __name__)


# ==================== SOLICITUDES DE SERVICIOS ====================

@servicios_bp.route('/solicitudes', methods=['POST'])
def crear_solicitud_servicio():
    """Crear nueva solicitud de servicio desde formulario público"""
    try:
        data = request.get_json()

        # Validaciones
        required_fields = ['servicio_id', 'nombre_cliente', 'email', 'mensaje']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400

        # Verificar que el servicio existe
        servicio = Servicio.query.get(data['servicio_id'])
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio no encontrado'
            }), 404

        # ✅ CORREGIDO: Usar campos que coinciden con el modelo
        solicitud = SolicitudServicio(
            servicio_id=data['servicio_id'],
            nombre_cliente=data['nombre_cliente'],  # ← Campo del modelo
            email=data['email'],                    # ← Campo del modelo
            telefono=data.get('telefono'),
            empresa=data.get('empresa'),
            mensaje=data['mensaje'],                # ← Campo del modelo
            estado='pendiente',
            # Campos de compatibilidad
            nombre_contacto=data.get('nombre_cliente'),
            email_contacto=data.get('email'),
            telefono_contacto=data.get('telefono'),
            area_servicio=data.get('area_servicio'),
            detalle=data.get('mensaje')
        )

        db.session.add(solicitud)
        db.session.commit()

        # Enviar email de notificación
        try:
            email_sender.send_service_request_email(solicitud, servicio)
        except Exception as email_error:
            print(f"❌ Error enviando email de servicio: {email_error}")

        return jsonify({
            'success': True,
            'message': 'Solicitud de servicio enviada correctamente',
            'solicitud': {
                'id': solicitud.id,
                'servicio_id': solicitud.servicio_id,
                'nombre_cliente': solicitud.nombre_cliente,
                'email': solicitud.email,
                'estado': solicitud.estado
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@servicios_bp.route('/solicitudes', methods=['GET'])
@jwt_required()
def listar_solicitudes_servicios():
    """Listar todas las solicitudes de servicios (admin)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        estado = request.args.get('estado')

        query = SolicitudServicio.query

        if estado:
            query = query.filter_by(estado=estado)

        solicitudes = query.order_by(SolicitudServicio.fecha_creacion.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        solicitudes_data = []
        for sol in solicitudes.items:
            servicio_nombre = getattr(sol.servicio, 'nombre', '') if sol.servicio else ''

            solicitudes_data.append({
                'id': sol.id,
                'servicio_id': sol.servicio_id,
                'servicio_nombre': servicio_nombre,
                'nombre_contacto': sol.nombre_contacto,
                'email_contacto': sol.email_contacto,
                'telefono_contacto': sol.telefono_contacto,
                'empresa': sol.empresa,
                'area_servicio': sol.area_servicio,
                'detalle': sol.detalle,
                'estado': sol.estado,
                'fecha_creacion': sol.fecha_creacion.isoformat() if sol.fecha_creacion else None
            })

        return jsonify({
            'success': True,
            'solicitudes': solicitudes_data,
            'total': solicitudes.total,
            'pages': solicitudes.pages,
            'current_page': page
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/solicitudes/<int:solicitud_id>', methods=['GET'])
@jwt_required()
def obtener_solicitud_servicio(solicitud_id):
    """Obtener solicitud de servicio específica"""
    try:
        solicitud = SolicitudServicio.query.get_or_404(solicitud_id)

        servicio_nombre = getattr(solicitud.servicio, 'nombre', '') if solicitud.servicio else ''

        return jsonify({
            'success': True,
            'solicitud': {
                'id': solicitud.id,
                'servicio_id': solicitud.servicio_id,
                'servicio_nombre': servicio_nombre,
                'nombre_contacto': solicitud.nombre_contacto,
                'email_contacto': solicitud.email_contacto,
                'telefono_contacto': solicitud.telefono_contacto,
                'empresa': solicitud.empresa,
                'area_servicio': solicitud.area_servicio,
                'detalle': solicitud.detalle,
                'estado': solicitud.estado,
                'fecha_creacion': solicitud.fecha_creacion.isoformat() if solicitud.fecha_creacion else None,
                'fecha_actualizacion': solicitud.fecha_actualizacion.isoformat() if solicitud.fecha_actualizacion else None
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/solicitudes/<int:solicitud_id>', methods=['PUT'])
@jwt_required()
def actualizar_solicitud_servicio(solicitud_id):
    """Actualizar estado de solicitud de servicio"""
    try:
        solicitud = SolicitudServicio.query.get_or_404(solicitud_id)
        data = request.get_json()

        if not data or 'estado' not in data:
            return jsonify({
                'success': False,
                'error': 'El campo estado es requerido'
            }), 400

        estados_validos = ['pendiente', 'en_proceso', 'completado', 'cancelado']
        if data['estado'] not in estados_validos:
            return jsonify({
                'success': False,
                'error': f'Estado inválido. Debe ser: {", ".join(estados_validos)}'
            }), 400

        solicitud.estado = data['estado']
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Solicitud actualizada a estado: {solicitud.estado}',
            'solicitud': {
                'id': solicitud.id,
                'estado': solicitud.estado
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/solicitudes/<int:solicitud_id>', methods=['DELETE'])
@jwt_required()
def eliminar_solicitud_servicio(solicitud_id):
    """Eliminar solicitud de servicio"""
    try:
        solicitud = SolicitudServicio.query.get_or_404(solicitud_id)
        db.session.delete(solicitud)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Solicitud de servicio eliminada correctamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== SERVICIOS ====================

@servicios_bp.route('/', methods=['GET'])
def listar_servicios():
    """Listar todos los servicios activos"""
    try:
        servicios = Servicio.query.filter_by(activo=True).all()

        servicios_data = []
        for serv in servicios:
            servicios_data.append({
                'id': serv.id,
                'nombre': getattr(serv, 'nombre', ''),
                'descripcion': getattr(serv, 'descripcion', ''),
                'precio_base': float(getattr(serv, 'precio_base', 0)),
                'categoria': getattr(serv, 'categoria', ''),
                'activo': getattr(serv, 'activo', True)
            })

        return jsonify({
            'success': True,
            'servicios': servicios_data
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/admin', methods=['GET'])
@jwt_required()
def listar_servicios_admin():
    """Listar todos los servicios (admin)"""
    try:
        servicios = Servicio.query.all()

        servicios_data = []
        for serv in servicios:
            servicios_data.append({
                'id': serv.id,
                'nombre': getattr(serv, 'nombre', ''),
                'descripcion': getattr(serv, 'descripcion', ''),
                'precio_base': float(getattr(serv, 'precio_base', 0)),
                'categoria': getattr(serv, 'categoria', ''),
                'activo': getattr(serv, 'activo', True)
            })

        return jsonify({
            'success': True,
            'servicios': servicios_data
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/', methods=['POST'])
@jwt_required()
def crear_servicio():
    """Crear nuevo servicio"""
    try:
        data = request.get_json()

        if not data or not data.get('nombre'):
            return jsonify({
                'success': False,
                'error': 'El nombre del servicio es requerido'
            }), 400

        servicio = Servicio(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            precio_base=data.get('precio_base', 0),
            categoria=data.get('categoria', 'general'),
            activo=data.get('activo', True)
        )

        db.session.add(servicio)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Servicio creado correctamente',
            'servicio': {
                'id': servicio.id,
                'nombre': servicio.nombre,
                'descripcion': servicio.descripcion,
                'precio_base': float(servicio.precio_base),
                'categoria': servicio.categoria,
                'activo': servicio.activo
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/<int:servicio_id>', methods=['PUT'])
@jwt_required()
def actualizar_servicio(servicio_id):
    """Actualizar servicio existente"""
    try:
        servicio = Servicio.query.get_or_404(servicio_id)
        data = request.get_json()

        if data.get('nombre'):
            servicio.nombre = data['nombre']
        if 'descripcion' in data:
            servicio.descripcion = data['descripcion']
        if 'precio_base' in data:
            servicio.precio_base = data['precio_base']
        if 'categoria' in data:
            servicio.categoria = data['categoria']
        if 'activo' in data:
            servicio.activo = data['activo']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Servicio actualizado correctamente',
            'servicio': {
                'id': servicio.id,
                'nombre': servicio.nombre,
                'descripcion': servicio.descripcion,
                'precio_base': float(servicio.precio_base),
                'categoria': servicio.categoria,
                'activo': servicio.activo
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/<int:servicio_id>', methods=['DELETE'])
@jwt_required()
def eliminar_servicio(servicio_id):
    """Eliminar servicio (lógicamente)"""
    try:
        servicio = Servicio.query.get_or_404(servicio_id)
        servicio.activo = False
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Servicio marcado como inactivo'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/estadisticas', methods=['GET'])
@jwt_required()
def estadisticas_servicios():
    """Estadísticas de servicios y solicitudes"""
    try:
        total_servicios = Servicio.query.filter_by(activo=True).count()
        total_solicitudes = SolicitudServicio.query.count()

        solicitudes_pendientes = SolicitudServicio.query.filter_by(estado='pendiente').count()
        solicitudes_completadas = SolicitudServicio.query.filter_by(estado='completado').count()

        return jsonify({
            'success': True,
            'estadisticas': {
                'total_servicios': total_servicios,
                'total_solicitudes': total_solicitudes,
                'solicitudes_pendientes': solicitudes_pendientes,
                'solicitudes_completadas': solicitudes_completadas
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500