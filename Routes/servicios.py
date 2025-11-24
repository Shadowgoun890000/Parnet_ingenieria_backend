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

        # ✅ CORREGIDO: Solo usar campos que existen en el modelo
        solicitud = SolicitudServicio(
            servicio_id=data['servicio_id'],
            nombre_cliente=data['nombre_cliente'],
            email=data['email'],
            telefono=data.get('telefono'),
            empresa=data.get('empresa'),
            mensaje=data['mensaje'],
            estado='pendiente'
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

            # ✅ CORREGIDO: Solo usar campos que existen en el modelo
            solicitudes_data.append({
                'id': sol.id,
                'servicio_id': sol.servicio_id,
                'servicio_nombre': servicio_nombre,
                'nombre_cliente': sol.nombre_cliente,
                'email': sol.email,
                'telefono': sol.telefono,
                'empresa': sol.empresa,
                'mensaje': sol.mensaje,
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

        # ✅ CORREGIDO: Solo usar campos que existen en el modelo
        return jsonify({
            'success': True,
            'solicitud': {
                'id': solicitud.id,
                'servicio_id': solicitud.servicio_id,
                'servicio_nombre': servicio_nombre,
                'nombre_cliente': solicitud.nombre_cliente,
                'email': solicitud.email,
                'telefono': solicitud.telefono,
                'empresa': solicitud.empresa,
                'mensaje': solicitud.mensaje,
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
                'nombre': serv.nombre,
                'descripcion': serv.descripcion,
                'area': serv.area,
                'imagen': serv.imagen,
                'caracteristicas': serv.caracteristicas,
                'orden': serv.orden,
                'activo': serv.activo
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
                'nombre': serv.nombre,
                'descripcion': serv.descripcion,
                'area': serv.area,
                'imagen': serv.imagen,
                'caracteristicas': serv.caracteristicas,
                'orden': serv.orden,
                'activo': serv.activo
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
            area=data.get('area', 'telecomunicaciones'),
            imagen=data.get('imagen'),
            caracteristicas=data.get('caracteristicas'),
            orden=data.get('orden', 0),
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
                'area': servicio.area,
                'imagen': servicio.imagen,
                'caracteristicas': servicio.caracteristicas,
                'orden': servicio.orden,
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
        if 'area' in data:
            servicio.area = data['area']
        if 'imagen' in data:
            servicio.imagen = data['imagen']
        if 'caracteristicas' in data:
            servicio.caracteristicas = data['caracteristicas']
        if 'orden' in data:
            servicio.orden = data['orden']
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
                'area': servicio.area,
                'imagen': servicio.imagen,
                'caracteristicas': servicio.caracteristicas,
                'orden': servicio.orden,
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