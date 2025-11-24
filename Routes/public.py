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

        query = Producto.query.filter_by(activo=True)

        if search:
            query = query.filter(
                or_(
                    Producto.nombre.ilike(f'%{search}%'),
                    Producto.descripcion_corta.ilike(f'%{search}%')
                )
            )

        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)

        if destacado is not None and hasattr(Producto, 'destacado'):
            query = query.filter_by(destacado=destacado)

        productos = query.order_by(Producto.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        productos_data = []
        for prod in productos.items:
            productos_data.append({
                'id': prod.id,
                'nombre': getattr(prod, 'nombre', ''),
                'descripcion': getattr(prod, 'descripcion', ''),
                'descripcion_corta': getattr(prod, 'descripcion_corta', ''),
                'precio': float(getattr(prod, 'precio', 0)),
                'estatus': getattr(prod, 'estatus', 'disponible'),
                'imagen_url': getattr(prod, 'imagen_url', ''),
                'categoria_id': getattr(prod, 'categoria_id', None),
                'stock': getattr(prod, 'stock', 0),
                'sku': getattr(prod, 'sku', f'PROD-{prod.id}'),
                'destacado': getattr(prod, 'destacado', False)
            })

        return jsonify({
            'success': True,
            'productos': productos_data,
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
            activo=True
        ).first()

        if not producto:
            return jsonify({
                'success': False,
                'error': 'Producto no encontrado'
            }), 404

        producto_data = {
            'id': producto.id,
            'nombre': getattr(producto, 'nombre', ''),
            'descripcion': getattr(producto, 'descripcion', ''),
            'descripcion_corta': getattr(producto, 'descripcion_corta', ''),
            'precio': float(getattr(producto, 'precio', 0)),
            'estatus': getattr(producto, 'estatus', 'disponible'),
            'imagen_url': getattr(producto, 'imagen_url', ''),
            'categoria_id': getattr(producto, 'categoria_id', None),
            'stock': getattr(producto, 'stock', 0),
            'sku': getattr(producto, 'sku', f'PROD-{producto.id}'),
            'destacado': getattr(producto, 'destacado', False)
        }

        return jsonify({
            'success': True,
            'producto': producto_data
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/productos/destacados', methods=['GET'])
def get_productos_destacados():
    """Obtener productos destacados"""
    try:
        limit = request.args.get('limit', 6, type=int)

        query = Producto.query.filter_by(activo=True)

        if hasattr(Producto, 'destacado'):
            query = query.filter_by(destacado=True)

        productos = query.order_by(Producto.id.desc()).limit(limit).all()

        productos_data = []
        for prod in productos:
            productos_data.append({
                'id': prod.id,
                'nombre': getattr(prod, 'nombre', ''),
                'descripcion_corta': getattr(prod, 'descripcion_corta', ''),
                'precio': float(getattr(prod, 'precio', 0)),
                'imagen_url': getattr(prod, 'imagen_url', ''),
                'destacado': getattr(prod, 'destacado', False)
            })

        return jsonify({
            'success': True,
            'productos': productos_data
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/categorias', methods=['GET'])
def get_categorias_public():
    """Obtener categorías para frontend público"""
    try:
        categorias = CategoriaProducto.query.filter_by(activo=True).all()

        categorias_data = []
        for cat in categorias:
            categorias_data.append({
                'id': cat.id,
                'nombre': getattr(cat, 'nombre', ''),
                'descripcion': getattr(cat, 'descripcion', ''),
                'activo': getattr(cat, 'activo', True)
            })

        return jsonify({
            'success': True,
            'categorias': categorias_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/servicios', methods=['GET'])
def obtener_servicios_publicos():
    """Lista pública de servicios para el frontend"""
    try:
        servicios = Servicio.query.filter_by(activo=True).all()

        servicios_data = []
        for serv in servicios:
            servicios_data.append({
                "id": serv.id,
                "nombre": getattr(serv, "nombre", ""),
                "descripcion": getattr(serv, "descripcion", ""),
                "precio_base": float(getattr(serv, "precio_base", 0)),
                "activo": getattr(serv, "activo", True)
            })

        return jsonify({
            "success": True,
            "servicios": servicios_data
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
        clientes = Cliente.query.filter_by(activo=True).all()

        clientes_data = []
        for cliente in clientes:
            clientes_data.append({
                'id': cliente.id,
                'nombre': getattr(cliente, 'nombre', ''),
                'logo_url': getattr(cliente, 'logo_url', ''),
                'activo': getattr(cliente, 'activo', True)
            })

        return jsonify({
            'success': True,
            'clientes': clientes_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@public_bp.route('/noticias', methods=['GET'])
def get_noticias_public():
    """Obtener noticias para frontend público"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 6, type=int)

        query = Noticia.query

        # Intentar filtrar por activas si existe el campo
        if hasattr(Noticia, 'activa'):
            query = query.filter_by(activa=True)

        # Intentar ordenar por fecha
        try:
            query = query.order_by(Noticia.fecha_publicacion.desc())
        except:
            query = query.order_by(Noticia.id.desc())

        noticias_pag = query.paginate(page=page, per_page=per_page, error_out=False)

        noticias_data = []
        for n in noticias_pag.items:
            noticias_data.append({
                "id": getattr(n, "id", None),
                "titulo": getattr(n, "titulo", "") or getattr(n, "titulo_noticia", ""),
                "resumen": getattr(n, "resumen", "") or getattr(n, "descripcion_corta", ""),
                "contenido": getattr(n, "contenido", "") or getattr(n, "cuerpo", ""),
                "fecha_publicacion": getattr(n, "fecha_publicacion", None),
                "visitas": getattr(n, "visitas", 0),
                "autor": getattr(n, "autor", "") or getattr(n, "creado_por", ""),
                "imagen_url": getattr(n, "imagen_url", "")
            })

        return jsonify({
            "success": True,
            "noticias": noticias_data,
            "total": noticias_pag.total,
            "pages": noticias_pag.pages,
            "current_page": noticias_pag.page
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@public_bp.route('/noticias/<int:noticia_id>', methods=['GET'])
def get_noticia_public(noticia_id):
    """Obtener noticia específica"""
    try:
        noticia = Noticia.query.get(noticia_id)

        if not noticia:
            return jsonify({
                "success": False,
                "error": "Noticia no encontrada"
            }), 404

        # Incrementar visitas si el campo existe
        if hasattr(noticia, 'visitas'):
            noticia.visitas = getattr(noticia, 'visitas', 0) + 1
            db.session.commit()

        noticia_data = {
            "id": getattr(noticia, "id", None),
            "titulo": getattr(noticia, "titulo", "") or getattr(noticia, "titulo_noticia", ""),
            "resumen": getattr(noticia, "resumen", "") or getattr(noticia, "descripcion_corta", ""),
            "contenido": getattr(noticia, "contenido", "") or getattr(noticia, "cuerpo", ""),
            "fecha_publicacion": getattr(noticia, "fecha_publicacion", None),
            "visitas": getattr(noticia, "visitas", 0),
            "autor": getattr(noticia, "autor", "") or getattr(noticia, "creado_por", ""),
            "imagen_url": getattr(noticia, "imagen_url", "")
        }

        return jsonify({
            "success": True,
            "noticia": noticia_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@public_bp.route('/noticias/recientes', methods=['GET'])
def get_noticias_recientes():
    """Obtener noticias más recientes"""
    try:
        limit = request.args.get('limit', 3, type=int)

        query = Noticia.query

        if hasattr(Noticia, 'activa'):
            query = query.filter_by(activa=True)

        try:
            query = query.order_by(Noticia.fecha_publicacion.desc())
        except:
            query = query.order_by(Noticia.id.desc())

        noticias = query.limit(limit).all()

        noticias_data = []
        for n in noticias:
            noticias_data.append({
                "id": getattr(n, "id", None),
                "titulo": getattr(n, "titulo", "") or getattr(n, "titulo_noticia", ""),
                "fecha_publicacion": getattr(n, "fecha_publicacion", None),
                "visitas": getattr(n, "visitas", 0),
            })

        return jsonify({
            "success": True,
            "noticias": noticias_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@public_bp.route('/search', methods=['GET'])
def search_global():
    """Búsqueda global en productos y servicios"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)

        if not query:
            return jsonify({
                'success': False,
                'error': 'Término de búsqueda requerido'
            }), 400

        # Buscar en productos
        productos = Producto.query.filter_by(activo=True).filter(
            or_(
                Producto.nombre.ilike(f'%{query}%'),
                Producto.descripcion_corta.ilike(f'%{query}%'),
                Producto.descripcion.ilike(f'%{query}%')
            )
        ).limit(limit).all()

        # Buscar en servicios
        servicios = Servicio.query.filter_by(activo=True).filter(
            or_(
                Servicio.nombre.ilike(f'%{query}%'),
                Servicio.descripcion.ilike(f'%{query}%')
            )
        ).limit(limit).all()

        productos_data = []
        for prod in productos:
            productos_data.append({
                'id': prod.id,
                'nombre': getattr(prod, 'nombre', ''),
                'descripcion_corta': getattr(prod, 'descripcion_corta', ''),
                'precio': float(getattr(prod, 'precio', 0)),
                'tipo': 'producto'
            })

        servicios_data = []
        for serv in servicios:
            servicios_data.append({
                'id': serv.id,
                'nombre': getattr(serv, 'nombre', ''),
                'descripcion': getattr(serv, 'descripcion', ''),
                'tipo': 'servicio'
            })

        return jsonify({
            'success': True,
            'resultados': {
                'productos': productos_data,
                'servicios': servicios_data,
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
            'nombre': 'PARNET INGENIERÍA S.A. DE C.V.',
            'descripcion': 'Soluciones Integrales en Telecomunicaciones (Voz y datos), eléctricas que resuelvan las necesidades empresariales con productos, aplicaciones, servicios y tecnología de punta.',
            'telefono': '+52 123 456 7890',
            'email': 'info@parnet.com',
            'direccion': 'Aguascalientes, México',
            'horario': 'Lunes a Viernes: 9:00 AM - 6:00 PM',
            'mision': 'Proporcionar soluciones integrales en telecomunicaciones y energía que satisfagan las necesidades de nuestros clientes con calidad y tecnología de vanguardia.',
            'vision': 'Ser la empresa líder en soluciones tecnológicas en México, reconocida por nuestra innovación y calidad de servicio.'
        }

        return jsonify({'success': True, 'info': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500