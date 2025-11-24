from flask import Blueprint, request, jsonify
from DataBase.models.producto import Producto, CategoriaProducto
from DataBase.models.servicio import Servicio
from DataBase.models.cliente import Cliente
from DataBase.models.noticia import Noticia
from DataBase.models.database import db
from sqlalchemy import or_

public_bp = Blueprint('public', __name__)


@public_bp.route('/productos', methods=['GET'])
def get_productos_public():
    """Obtener productos para el frontend público"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        search = request.args.get('search', '')
        categoria_id = request.args.get('categoria_id', type=int)
        destacado = request.args.get('destacado', type=bool)

        query = Producto.query.filter_by(activo=True, estatus='disponible')

        if search:
            query = query.filter(
                or_(
                    Producto.nombre.ilike(f'%{search}%'),
                    Producto.descripcion_corta.ilike(f'%{search}%'),
                    Producto.sku.ilike(f'%{search}%')
                )
            )

        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)

        if destacado is not None:
            query = query.filter_by(destacado=destacado)

        productos = query.order_by(Producto.destacado.desc(), Producto.fecha_creacion.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'success': True,
            'productos': [prod.to_dict() for prod in productos.items],
            'total': productos.total,
            'pages': productos.pages,
            'current_page': page
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/productos/<int:producto_id>', methods=['GET'])
def get_producto_public(producto_id):
    """Obtener producto específico para frontend público"""
    try:
        producto = Producto.query.filter_by(
            id=producto_id,
            activo=True,
            estatus='disponible'
        ).first_or_404()

        return jsonify({'success': True, 'producto': producto.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/productos/destacados', methods=['GET'])
def get_productos_destacados():
    """Obtener productos destacados"""
    try:
        limit = request.args.get('limit', 6, type=int)

        productos = Producto.query.filter_by(
            activo=True,
            estatus='disponible',
            destacado=True
        ).order_by(Producto.fecha_creacion.desc()).limit(limit).all()

        return jsonify({
            'success': True,
            'productos': [prod.to_dict() for prod in productos]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/categorias', methods=['GET'])
def get_categorias_public():
    """Obtener categorías para frontend público"""
    try:
        categorias = CategoriaProducto.query.filter_by(activo=True).order_by(
            CategoriaProducto.orden.asc()
        ).all()

        return jsonify({
            'success': True,
            'categorias': [cat.to_dict() for cat in categorias]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== SERVICIOS PÚBLICOS ====================

# ==================== SERVICIOS PÚBLICOS ====================

@public_bp.route('/servicios', methods=['GET'])
def obtener_servicios_publicos():
    """Lista pública de servicios para el frontend"""
    try:
        servicios = Servicio.query.all()  # si más adelante tienes 'activo', puedes filtrar por eso

        return jsonify({
            "success": True,
            "servicios": [s.to_dict() for s in servicios]
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@public_bp.route('/clientes', methods=['GET'])
def get_clientes_public():
    """Obtener clientes para frontend público"""
    try:
        clientes = Cliente.query.filter_by(activo=True).order_by(
            Cliente.orden.asc()
        ).all()

        return jsonify({
            'success': True,
            'clientes': [cliente.to_dict() for cliente in clientes]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/noticias', methods=['GET'])
def get_noticias_public():
    """Obtener noticias para frontend público"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 6, type=int)

        noticias = Noticia.query.filter_by(activa=True).order_by(
            Noticia.fecha_publicacion.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'noticias': [noticia.to_dict() for noticia in noticias.items],
            'total': noticias.total,
            'pages': noticias.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/noticias/<int:noticia_id>', methods=['GET'])
def get_noticia_public(noticia_id):
    """Obtener noticia específica e incrementar visitas"""
    try:
        noticia = Noticia.query.filter_by(id=noticia_id, activa=True).first_or_404()

        # Incrementar contador de visitas
        noticia.visitas += 1
        db.session.commit()

        return jsonify({'success': True, 'noticia': noticia.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/noticias/recientes', methods=['GET'])
def get_noticias_recientes():
    """Obtener noticias más recientes (para sidebar o home)"""
    try:
        limit = request.args.get('limit', 3, type=int)

        noticias = Noticia.query.filter_by(activa=True).order_by(
            Noticia.fecha_publicacion.desc()
        ).limit(limit).all()

        return jsonify({
            'success': True,
            'noticias': [noticia.to_dict() for noticia in noticias]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/search', methods=['GET'])
def search_global():
    """Búsqueda global en productos y servicios"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)

        if not query:
            return jsonify({'success': False, 'error': 'Término de búsqueda requerido'}), 400

        # Buscar en productos
        productos = Producto.query.filter_by(activo=True, estatus='disponible').filter(
            or_(
                Producto.nombre.ilike(f'%{query}%'),
                Producto.descripcion_corta.ilike(f'%{query}%'),
                Producto.descripcion_larga.ilike(f'%{query}%')
            )
        ).limit(limit).all()

        # Buscar en servicios
        servicios = Servicio.query.filter_by(activo=True).filter(
            or_(
                Servicio.nombre.ilike(f'%{query}%'),
                Servicio.descripcion.ilike(f'%{query}%')
            )
        ).limit(limit).all()

        return jsonify({
            'success': True,
            'resultados': {
                'productos': [prod.to_dict() for prod in productos],
                'servicios': [serv.to_dict() for serv in servicios],
                'total_productos': len(productos),
                'total_servicios': len(servicios)
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/info', methods=['GET'])
def get_info_empresa():
    """Información básica de la empresa para el frontend"""
    try:
        info = {
            'nombre': 'PARNET Ingeniería S.A. de C.V.',
            'descripcion': 'Soluciones Integrales en Telecomunicaciones (Voz y datos), eléctricas que resuelvan las necesidades empresariales con productos, aplicaciones, servicios y tecnología de punta.',
            'telefono': '+52 123 456 7890',
            'email': 'info@parnet.com',
            'direccion': 'Aguascalientes, México',
            'horario': 'Lunes a Viernes: 9:00 AM - 6:00 PM',
            'redes_sociales': {
                'facebook': 'https://facebook.com/parnet',
                'twitter': 'https://twitter.com/parnet',
                'linkedin': 'https://linkedin.com/company/parnet'
            }
        }

        return jsonify({'success': True, 'info': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500