from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_
from DataBase.models.producto import Producto, CategoriaProducto
from DataBase.models.database import db

productos_bp = Blueprint('productos', __name__)


def _producto_to_dict(p):
    """Helper para serializar producto a dict"""
    try:
        categoria_nombre = None
        if hasattr(p, "categoria") and p.categoria is not None:
            categoria_nombre = getattr(p.categoria, "nombre", None)

        return {
            "id": p.id,
            "nombre": getattr(p, "nombre", ""),
            "descripcion": getattr(p, "descripcion", ""),
            "descripcion_corta": getattr(p, "descripcion_corta", None),
            "precio": float(getattr(p, "precio", 0) or 0),
            "estatus": getattr(p, "estatus", "disponible"),
            "imagen_url": getattr(p, "imagen_url", None),
            "categoria_id": getattr(p, "categoria_id", None),
            "categoria": categoria_nombre,
            "activo": getattr(p, "activo", True),
            "stock": getattr(p, "stock", 0),
            "sku": getattr(p, "sku", f"PROD-{p.id}"),
            "destacado": getattr(p, "destacado", False)
        }
    except Exception as e:
        return {
            "id": p.id,
            "nombre": "Error serializando producto",
            "error": str(e)
        }


# ==================== ENDPOINTS PÚBLICOS ====================

@productos_bp.route('/public', methods=['GET'])
def listar_productos_publicos():
    """Listado público de productos para el frontend"""
    try:
        # Filtros
        texto = request.args.get('q', '').strip()
        categoria_id = request.args.get('categoria_id', type=int)
        destacado = request.args.get('destacado', type=bool)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)

        # Query base
        query = Producto.query.filter_by(activo=True)

        # Filtro por texto
        if texto:
            like_text = f"%{texto}%"
            filtros = [Producto.nombre.ilike(like_text)]
            if hasattr(Producto, "descripcion"):
                filtros.append(Producto.descripcion.ilike(like_text))
            if hasattr(Producto, "descripcion_corta"):
                filtros.append(Producto.descripcion_corta.ilike(like_text))
            if hasattr(Producto, "sku"):
                filtros.append(Producto.sku.ilike(like_text))
            query = query.filter(or_(*filtros))

        # Filtro por categoría
        if categoria_id and hasattr(Producto, "categoria_id"):
            query = query.filter_by(categoria_id=categoria_id)

        # Filtro por destacado
        if destacado is not None and hasattr(Producto, "destacado"):
            query = query.filter_by(destacado=destacado)

        # Paginación
        productos_pag = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        resultado = []
        for p in productos_pag.items:
            categoria_nombre = None
            if hasattr(p, "categoria") and getattr(p, "categoria") is not None:
                categoria_nombre = getattr(p.categoria, "nombre", None)

            producto_dict = {
                "id": p.id,
                "nombre": getattr(p, "nombre", ""),
                "descripcion": getattr(p, "descripcion", ""),
                "descripcion_corta": getattr(p, "descripcion_corta", ""),
                "precio": float(getattr(p, "precio", 0) or 0),
                "estatus": getattr(p, "estatus", "disponible"),
                "imagen_url": getattr(p, "imagen_url", ""),
                "categoria": categoria_nombre,
                "stock": getattr(p, "stock", 0),
                "sku": getattr(p, "sku", f"PROD-{p.id}"),
                "destacado": getattr(p, "destacado", False)
            }
            resultado.append(producto_dict)

        return jsonify({
            "success": True,
            "productos": resultado,
            "total": productos_pag.total,
            "pages": productos_pag.pages,
            "current_page": page
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@productos_bp.route('/public/<int:producto_id>', methods=['GET'])
def obtener_producto_publico(producto_id):
    """Obtener producto específico para frontend público"""
    try:
        producto = Producto.query.filter_by(
            id=producto_id,
            activo=True
        ).first()

        if not producto:
            return jsonify({
                "success": False,
                "error": "Producto no encontrado"
            }), 404

        return jsonify({
            "success": True,
            "producto": _producto_to_dict(producto)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@productos_bp.route('/public/destacados', methods=['GET'])
def obtener_productos_destacados():
    """Obtener productos destacados"""
    try:
        limit = request.args.get('limit', 6, type=int)

        query = Producto.query.filter_by(activo=True)

        # Si existe el campo destacado, filtrar por él
        if hasattr(Producto, 'destacado'):
            query = query.filter_by(destacado=True)

        productos = query.limit(limit).all()

        return jsonify({
            "success": True,
            "productos": [_producto_to_dict(p) for p in productos]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ENDPOINTS DE ADMIN ====================

@productos_bp.route('/', methods=['GET'])
@jwt_required()
def listar_productos_admin():
    """Listado de productos para administración"""
    try:
        productos = Producto.query.all()
        return jsonify({
            "success": True,
            "data": [_producto_to_dict(p) for p in productos]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@productos_bp.route('/', methods=['POST'])
@jwt_required()
def crear_producto():
    """Crear un nuevo producto"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Datos JSON requeridos"
            }), 400

        # Validar campos requeridos
        if not data.get("nombre"):
            return jsonify({
                "success": False,
                "error": "El nombre del producto es requerido"
            }), 400

        producto = Producto(
            nombre=data.get("nombre"),
            descripcion=data.get("descripcion", ""),
            descripcion_corta=data.get("descripcion_corta", ""),
            precio=data.get("precio", 0),
            estatus=data.get("estatus", "disponible"),
            imagen_url=data.get("imagen_url"),
            categoria_id=data.get("categoria_id"),
            activo=data.get("activo", True),
            stock=data.get("stock", 0),
            sku=data.get("sku", f"PROD-{Producto.query.count() + 1}"),
            destacado=data.get("destacado", False)
        )

        db.session.add(producto)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Producto creado correctamente",
            "data": _producto_to_dict(producto)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@productos_bp.route('/<int:producto_id>', methods=['GET'])
@jwt_required()
def obtener_producto(producto_id):
    """Obtener detalle de un producto (admin)"""
    try:
        producto = Producto.query.get_or_404(producto_id)
        return jsonify({
            "success": True,
            "data": _producto_to_dict(producto)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@productos_bp.route('/<int:producto_id>', methods=['PUT'])
@jwt_required()
def actualizar_producto(producto_id):
    """Actualizar un producto existente"""
    try:
        producto = Producto.query.get_or_404(producto_id)
        data = request.get_json() or {}

        # Actualizar campos
        campos = ['nombre', 'descripcion', 'descripcion_corta', 'precio',
                  'estatus', 'imagen_url', 'categoria_id', 'activo', 'stock',
                  'sku', 'destacado']

        for campo in campos:
            if campo in data:
                setattr(producto, campo, data[campo])

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Producto actualizado correctamente",
            "data": _producto_to_dict(producto)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@productos_bp.route('/<int:producto_id>', methods=['DELETE'])
@jwt_required()
def eliminar_producto(producto_id):
    """Eliminar (lógicamente) un producto"""
    try:
        producto = Producto.query.get_or_404(producto_id)

        if hasattr(producto, "activo"):
            producto.activo = False
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Producto marcado como inactivo"
            }), 200
        else:
            db.session.delete(producto)
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Producto eliminado físicamente"
            }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== CATEGORÍAS ====================

@productos_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """Listar categorías de productos"""
    try:
        categorias = CategoriaProducto.query.filter_by(activo=True).all()

        categorias_data = []
        for cat in categorias:
            categorias_data.append({
                "id": cat.id,
                "nombre": getattr(cat, "nombre", ""),
                "descripcion": getattr(cat, "descripcion", ""),
                "activo": getattr(cat, "activo", True)
            })

        return jsonify({
            "success": True,
            "categorias": categorias_data
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500