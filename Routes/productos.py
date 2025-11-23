from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from DataBase.models.producto import Producto, CategoriaProducto
from DataBase.models.database import db
from sqlalchemy import or_
from Utils.pdf_generator import PDFGenerator
import tempfile
from datetime import datetime

productos_bp = Blueprint('productos', __name__)


# ... (código existente se mantiene igual) ...

@productos_bp.route('/<int:producto_id>/ficha-pdf', methods=['GET'])
def generar_ficha_producto_pdf(producto_id):
    """Generar ficha técnica de producto en PDF (pública)"""
    try:
        producto = Producto.query.filter_by(
            id=producto_id,
            activo=True,
            estatus='disponible'
        ).first_or_404()

        # Generar PDF
        pdf = PDFGenerator.generate_product_sheet(producto)

        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            pdf_output = PDFGenerator.get_pdf_bytes(pdf)
            tmp.write(pdf_output)
            tmp_path = tmp.name

        filename = f"ficha_tecnica_{producto.sku}.pdf"

        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@productos_bp.route('/reporte-pdf', methods=['GET'])
@jwt_required()
def generar_reporte_productos_pdf():
    """Generar reporte de productos en PDF (solo administradores)"""
    try:
        # Obtener todos los productos activos
        productos = Producto.query.filter_by(activo=True).all()

        # Generar PDF
        pdf = PDFGenerator.generate_products_report(productos)

        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            pdf_output = PDFGenerator.get_pdf_bytes(pdf)
            tmp.write(pdf_output)
            tmp_path = tmp.name

        filename = f"reporte_productos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500