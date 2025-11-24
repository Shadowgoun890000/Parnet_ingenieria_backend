from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from DataBase.models.producto import Producto, CategoriaProducto
from DataBase.models.servicio import Servicio, SolicitudServicio
from DataBase.models.cliente import Cliente
from DataBase.models.contacto import Contacto, Sugerencia
from DataBase.models.noticia import Noticia
from DataBase.models.database import db
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/estadisticas', methods=['GET'])
@jwt_required()
def get_estadisticas():
    """Obtener estadísticas para el dashboard del admin"""
    try:
        # Productos por categoría
        productos_por_categoria = []
        try:
            productos_por_categoria = db.session.query(
                CategoriaProducto.nombre,
                db.func.count(Producto.id)
            ).join(Producto).filter(
                Producto.activo == True
            ).group_by(CategoriaProducto.id).all()
        except Exception:
            # Si falla, usar datos vacíos
            pass

        # Servicios más solicitados
        servicios_solicitados = []
        try:
            servicios_solicitados = db.session.query(
                Servicio.nombre,
                db.func.count(SolicitudServicio.id)
            ).join(SolicitudServicio).group_by(Servicio.id).all()
        except Exception:
            pass

        # Solicitudes por estado
        solicitudes_por_estado = []
        try:
            solicitudes_por_estado = db.session.query(
                SolicitudServicio.estado,
                db.func.count(SolicitudServicio.id)
            ).group_by(SolicitudServicio.estado).all()
        except Exception:
            pass

        # Productos por estatus
        productos_por_estatus = []
        try:
            productos_por_estatus = db.session.query(
                Producto.estatus,
                db.func.count(Producto.id)
            ).filter(Producto.activo == True).group_by(Producto.estatus).all()
        except Exception:
            pass

        # Estadísticas generales
        total_productos = Producto.query.filter_by(activo=True).count()
        total_servicios = Servicio.query.filter_by(activo=True).count()
        total_clientes = Cliente.query.filter_by(activo=True).count()
        total_contactos = Contacto.query.count()
        total_sugerencias = Sugerencia.query.count()
        total_noticias = Noticia.query.filter_by(activa=True).count()

        # Solicitudes pendientes
        solicitudes_pendientes = 0
        try:
            solicitudes_pendientes = SolicitudServicio.query.filter_by(estado='pendiente').count()
        except Exception:
            pass

        # Productos agotados
        productos_agotados = 0
        try:
            productos_agotados = Producto.query.filter_by(estatus='agotado', activo=True).count()
        except Exception:
            pass

        # Estadísticas de los últimos 30 días
        fecha_limite = datetime.utcnow() - timedelta(days=30)

        nuevas_solicitudes = 0
        nuevos_contactos = 0

        try:
            nuevas_solicitudes = SolicitudServicio.query.filter(
                SolicitudServicio.fecha_creacion >= fecha_limite
            ).count()

            nuevos_contactos = Contacto.query.filter(
                Contacto.fecha_creacion >= fecha_limite
            ).count()
        except Exception:
            pass

        return jsonify({
            'success': True,
            'productos_por_categoria': [
                {'categoria': cat, 'cantidad': cant}
                for cat, cant in productos_por_categoria
            ],
            'servicios_solicitados': [
                {'servicio': serv, 'solicitudes': cant}
                for serv, cant in servicios_solicitados
            ],
            'solicitudes_por_estado': [
                {'estado': est, 'cantidad': cant}
                for est, cant in solicitudes_por_estado
            ],
            'productos_por_estatus': [
                {'estatus': est, 'cantidad': cant}
                for est, cant in productos_por_estatus
            ],
            'estadisticas_generales': {
                'total_productos': total_productos,
                'total_servicios': total_servicios,
                'total_clientes': total_clientes,
                'total_contactos': total_contactos,
                'total_sugerencias': total_sugerencias,
                'total_noticias': total_noticias,
                'solicitudes_pendientes': solicitudes_pendientes,
                'productos_agotados': productos_agotados,
                'nuevas_solicitudes_30d': nuevas_solicitudes,
                'nuevos_contactos_30d': nuevos_contactos
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/actividad-reciente', methods=['GET'])
@jwt_required()
def get_actividad_reciente():
    """Obtener actividad reciente para el dashboard"""
    try:
        # Últimas solicitudes de servicio
        ultimas_solicitudes = []
        try:
            ultimas_solicitudes = SolicitudServicio.query.order_by(
                SolicitudServicio.fecha_creacion.desc()
            ).limit(5).all()
        except Exception:
            pass

        # Últimos contactos
        ultimos_contactos = Contacto.query.order_by(
            Contacto.fecha_creacion.desc()
        ).limit(5).all()

        # Últimas sugerencias
        ultimas_sugerencias = Sugerencia.query.order_by(
            Sugerencia.fecha_creacion.desc()
        ).limit(5).all()

        # Productos con stock bajo (menos de 10 unidades)
        productos_stock_bajo = []
        try:
            productos_stock_bajo = Producto.query.filter(
                Producto.stock < 10,
                Producto.activo == True,
                Producto.estatus == 'disponible'
            ).order_by(Producto.stock.asc()).limit(5).all()
        except Exception:
            pass

        return jsonify({
            'success': True,
            'ultimas_solicitudes': [sol.to_dict() for sol in ultimas_solicitudes],
            'ultimos_contactos': [cont.to_dict() for cont in ultimos_contactos],
            'ultimas_sugerencias': [sug.to_dict() for sug in ultimas_sugerencias],
            'productos_stock_bajo': [prod.to_dict() for prod in productos_stock_bajo]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/resumen', methods=['GET'])
@jwt_required()
def get_resumen():
    """Resumen rápido para el dashboard"""
    try:
        total_productos = Producto.query.filter_by(activo=True).count()
        total_servicios = Servicio.query.filter_by(activo=True).count()
        total_clientes = Cliente.query.filter_by(activo=True).count()
        total_contactos = Contacto.query.count()

        # Contactos de hoy
        hoy = datetime.utcnow().date()
        contactos_hoy = Contacto.query.filter(
            db.func.date(Contacto.fecha_creacion) == hoy
        ).count()

        return jsonify({
            'success': True,
            'resumen': {
                'productos': total_productos,
                'servicios': total_servicios,
                'clientes': total_clientes,
                'contactos_total': total_contactos,
                'contactos_hoy': contactos_hoy
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500