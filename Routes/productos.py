# Routes/productos.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from DataBase.models.producto import Producto, CategoriaProducto
from DataBase.models.database import db

# Este blueprint se registra en app.py como:
# app.register_blueprint(productos_bp, url_prefix='/api/productos')
productos_bp = Blueprint('productos', __name__)


# ============================================================
# Helper para serializar un producto a dict (JSON)
# ============================================================
def _producto_to_dict(p: Producto):
    categoria_nombre = None
    if hasattr(p, "categoria") and p.categoria is not None:
        categoria_nombre = getattr(p.categoria, "nombre", None)

    return {
        "id": p.id,
        "nombre": getattr(p, "nombre", ""),
        "descripcion": getattr(p, "descripcion", ""),
        "descripcion_corta": getattr(p, "descripcion_corta", None),
        "precio": float(getattr(p, "precio", 0) or 0),
        "estatus": getattr(p, "estatus", ""),
        "imagen_url": getattr(p, "imagen_url", None),
        "categoria_id": getattr(p, "categoria_id", None),
        "categoria": categoria_nombre,
        "activo": getattr(p, "activo", True),
    }


# ============================================================
# 1) ENDPOINT PÚBLICO: LISTADO DE PRODUCTOS (JSON)
#    Ruta final: GET /api/productos/public
# ============================================================
@productos_bp.route('/public', methods=['GET'])
def listar_productos_publicos():
    """
    Listado público de productos para el frontend.
    Lo usa productos.html / productos.js.
    """
    try:
        # Si el modelo tiene campo 'activo', filtramos por activos
        try:
            query = Producto.query.filter_by(activo=True)
        except Exception:
            query = Producto.query

        texto = request.args.get('q', type=str, default='').strip()
        categoria_id = request.args.get('categoria_id', type=int)

        # Filtro por texto (nombre + descripción si existe)
        if texto:
            like_text = f"%{texto}%"
            filtros = [Producto.nombre.ilike(like_text)]
            if hasattr(Producto, "descripcion"):
                filtros.append(Producto.descripcion.ilike(like_text))
            if hasattr(Producto, "descripcion_corta"):
                filtros.append(Producto.descripcion_corta.ilike(like_text))
            query = query.filter(or_(*filtros))

        # Filtro por categoría (si el modelo tiene categoria_id)
        if categoria_id and hasattr(Producto, "categoria_id"):
            query = query.filter_by(categoria_id=categoria_id)

        productos = query.all()

        resultado = []
        for p in productos:
            categoria_nombre = None
            if hasattr(p, "categoria") and getattr(p, "categoria") is not None:
                categoria_nombre = getattr(p.categoria, "nombre", None)

            nombre = getattr(p, "nombre", "")
            descripcion_corta = getattr(p, "descripcion_corta", None)
            descripcion = descripcion_corta or getattr(p, "descripcion", "") or ""
            precio = getattr(p, "precio", 0) or 0
            estatus = getattr(p, "estatus", "") or ""
            imagen_url = getattr(p, "imagen_url", "") or ""

            resultado.append({
                "id": p.id,
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": float(precio),
                "estatus": estatus,
                "imagen_url": imagen_url,
                "categoria": categoria_nombre
            })

        return jsonify(resultado), 200

    except Exception as e:
        # Para depuración: devolvemos el error en el JSON
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# 2) ENDPOINTS PRIVADOS: CRUD DE PRODUCTOS (ADMIN)
#    Rutas finales:
#      GET    /api/productos/          → lista admin
#      POST   /api/productos/          → crear
#      GET    /api/productos/<id>      → detalle
#      PUT    /api/productos/<id>      → actualizar
#      DELETE /api/productos/<id>      → baja lógica
# ============================================================

@productos_bp.route('/', methods=['GET'])
@jwt_required()
def listar_productos_admin():
    """
    Listado de productos para administración.
    Ruta final: GET /api/productos/
    """
    try:
        productos = Producto.query.all()
        data = [_producto_to_dict(p) for p in productos]
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@productos_bp.route('/', methods=['POST'])
@jwt_required()
def crear_producto():
    """
    Crear un nuevo producto.
    Ruta final: POST /api/productos/
    Body JSON esperado (ejemplo):
    {
      "nombre": "Switch 24p",
      "descripcion": "Switch administrable...",
      "descripcion_corta": "Switch 24p GbE",
      "precio": 1234.56,
      "estatus": "disponible",
      "imagen_url": "/static/img/switch01.png",
      "categoria_id": 1,
      "activo": true
    }
    """
    try:
        data = request.get_json() or {}

        producto = Producto(
            nombre=data.get("nombre"),
            descripcion=data.get("descripcion"),
            descripcion_corta=data.get("descripcion_corta"),
            precio=data.get("precio", 0),
            estatus=data.get("estatus", "disponible"),
            imagen_url=data.get("imagen_url"),
            categoria_id=data.get("categoria_id"),
            activo=data.get("activo", True)
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
    """
    Obtener detalle de un producto (admin).
    Ruta final: GET /api/productos/<id>
    """
    try:
        producto = Producto.query.get_or_404(producto_id)
        return jsonify({"success": True, "data": _producto_to_dict(producto)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@productos_bp.route('/<int:producto_id>', methods=['PUT'])
@jwt_required()
def actualizar_producto(producto_id):
    """
    Actualizar un producto existente.
    Ruta final: PUT /api/productos/<id>
    """
    try:
        producto = Producto.query.get_or_404(producto_id)
        data = request.get_json() or {}

        producto.nombre = data.get("nombre", producto.nombre)
        producto.descripcion = data.get("descripcion", producto.descripcion)
        producto.descripcion_corta = data.get("descripcion_corta", producto.descripcion_corta)
        producto.precio = data.get("precio", producto.precio)
        producto.estatus = data.get("estatus", producto.estatus)
        producto.imagen_url = data.get("imagen_url", producto.imagen_url)
        producto.categoria_id = data.get("categoria_id", producto.categoria_id)
        producto.activo = data.get("activo", producto.activo)

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
    """
    Eliminar (lógicamente) un producto.
    Ruta final: DELETE /api/productos/<id>
    """
    try:
        producto = Producto.query.get_or_404(producto_id)

        # Eliminación lógica
        if hasattr(producto, "activo"):
            producto.activo = False
        else:
            # Si no tienes campo 'activo', podrías borrar físicamente:
            db.session.delete(producto)
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Producto eliminado físicamente (no hay campo 'activo')"
            }), 200

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Producto marcado como inactivo"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
