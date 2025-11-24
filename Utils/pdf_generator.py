from fpdf import FPDF
from datetime import datetime
import os
import tempfile


class ParnetPDF(FPDF):
    """Clase personalizada para generar PDFs en Parnet Ingeniería"""

    def header(self):
        # Logo - actualizado para usar la nueva estructura de static
        logo_path = 'static/assets/img/logotipo.png'
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)

        # Tipo de letra Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Movernos a la derecha
        self.cell(80)
        # Título
        self.cell(30, 10, 'PARNET INGENIERIA S.A. DE C.V.', 0, 0, 'C')
        # Salto de línea
        self.ln(20)

    def footer(self):
        # Posición a 1.5 cm del final
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Número de página
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def chapter_title(self, title):
        # Arial 12
        self.set_font('Arial', 'B', 12)
        # Color de fondo
        self.set_fill_color(200, 220, 255)
        # Título
        self.cell(0, 6, title, 0, 1, 'L', 1)
        # Salto de línea
        self.ln(4)

    def chapter_body(self, body):
        # Times 12
        self.set_font('Arial', '', 12)
        # Texto justificado
        self.multi_cell(0, 10, body)
        # Salto de línea
        self.ln()


class PDFGenerator:
    """Generador de PDF para diferentes tipos de documentos"""

    @staticmethod
    def generate_product_sheet(product):
        """Generar ficha técnica de producto"""
        pdf = ParnetPDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        # Título principal
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'FICHA TÉCNICA DE PRODUCTO', 0, 1, 'C')
        pdf.ln(10)

        # Información básica del producto
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'Nombre:', 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, getattr(product, 'nombre', 'N/A'), 0, 1)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'SKU:', 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, getattr(product, 'sku', f'PROD-{product.id}'), 0, 1)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'Precio:', 0, 0)
        pdf.set_font('Arial', '', 12)
        precio = float(getattr(product, 'precio', 0))
        pdf.cell(0, 10, f'${precio:,.2f} MXN', 0, 1)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'Stock:', 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, str(getattr(product, 'stock', 0)), 0, 1)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'Estado:', 0, 0)
        pdf.set_font('Arial', '', 12)
        estatus = getattr(product, 'estatus', 'disponible')
        pdf.cell(0, 10, estatus, 0, 1)
        pdf.ln(10)

        # Descripción
        descripcion = getattr(product, 'descripcion', '') or getattr(product, 'descripcion_larga', '')
        if descripcion:
            pdf.chapter_title('DESCRIPCIÓN')
            pdf.multi_cell(0, 10, descripcion)
            pdf.ln(10)

        # Descripción corta
        descripcion_corta = getattr(product, 'descripcion_corta', '')
        if descripcion_corta:
            pdf.chapter_title('DESCRIPCIÓN CORTA')
            pdf.multi_cell(0, 10, descripcion_corta)
            pdf.ln(10)

        # Categoría
        categoria_nombre = None
        if hasattr(product, 'categoria') and product.categoria:
            categoria_nombre = getattr(product.categoria, 'nombre', '')
        if categoria_nombre:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(40, 10, 'Categoría:', 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, categoria_nombre, 0, 1)
            pdf.ln(5)

        # Información de contacto
        pdf.ln(10)
        pdf.chapter_title('INFORMACIÓN DE CONTACTO')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, 'PARNET INGENIERÍA S.A. DE C.V.', 0, 1)
        pdf.cell(0, 8, 'Teléfono: +52 123 456 7890', 0, 1)
        pdf.cell(0, 8, 'Email: info@parnet.com', 0, 1)
        pdf.cell(0, 8, 'Web: www.parnet.com', 0, 1)
        pdf.cell(0, 8, f'Generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1)

        return pdf

    @staticmethod
    def generate_suggestions_report(suggestions):
        """Generar reporte de sugerencias en PDF"""
        pdf = ParnetPDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        # Título
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'REPORTE DE SUGERENCIAS', 0, 1, 'C')
        pdf.ln(10)

        # Información del reporte
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f'Total de sugerencias: {len(suggestions)}', 0, 1)
        pdf.cell(0, 8, f'Fecha de generación: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1)
        pdf.ln(10)

        # Tabla de sugerencias
        for i, sugerencia in enumerate(suggestions, 1):
            pdf.chapter_title(f'SUGERENCIA #{i}')

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Nombre:', 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, getattr(sugerencia, 'nombre', 'N/A'), 0, 1)

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Email:', 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, getattr(sugerencia, 'email', 'N/A'), 0, 1)

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Asunto:', 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, getattr(sugerencia, 'asunto', 'Sin asunto'), 0, 1)

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Fecha:', 0, 0)
            pdf.set_font('Arial', '', 10)
            fecha = getattr(sugerencia, 'fecha_creacion', datetime.now())
            if hasattr(fecha, 'strftime'):
                fecha_str = fecha.strftime("%d/%m/%Y %H:%M")
            else:
                fecha_str = str(fecha)
            pdf.cell(0, 8, fecha_str, 0, 1)

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Mensaje:', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 8, getattr(sugerencia, 'mensaje', 'Sin mensaje'))

            if i < len(suggestions):
                pdf.ln(5)
                pdf.cell(0, 1, '', 'T')  # Línea separadora
                pdf.ln(5)

        return pdf

    @staticmethod
    def generate_products_report(products):
        """Generar reporte de productos en PDF"""
        pdf = ParnetPDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        # Título
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'REPORTE DE PRODUCTOS', 0, 1, 'C')
        pdf.ln(10)

        # Estadísticas
        total_productos = len(products)
        disponibles = len([p for p in products if getattr(p, 'estatus', '') == 'disponible'])
        agotados = len([p for p in products if getattr(p, 'estatus', '') == 'agotado'])

        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f'Total de productos: {total_productos}', 0, 1)
        pdf.cell(0, 8, f'Disponibles: {disponibles}', 0, 1)
        pdf.cell(0, 8, f'Agotados: {agotados}', 0, 1)
        pdf.cell(0, 8, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1)
        pdf.ln(10)

        # Tabla de productos
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(80, 10, 'Producto', 1, 0, 'C')
        pdf.cell(30, 10, 'SKU', 1, 0, 'C')
        pdf.cell(30, 10, 'Precio', 1, 0, 'C')
        pdf.cell(20, 10, 'Stock', 1, 0, 'C')
        pdf.cell(30, 10, 'Estado', 1, 1, 'C')

        pdf.set_font('Arial', '', 9)
        for producto in products:
            # Nombre (truncado si es muy largo)
            nombre = getattr(producto, 'nombre', 'N/A')
            nombre = nombre[:35] + '...' if len(nombre) > 35 else nombre

            sku = getattr(producto, 'sku', f'PROD-{producto.id}')
            precio = float(getattr(producto, 'precio', 0))
            stock = getattr(producto, 'stock', 0)
            estatus = getattr(producto, 'estatus', 'desconocido')

            pdf.cell(80, 8, nombre, 1, 0)
            pdf.cell(30, 8, sku, 1, 0, 'C')
            pdf.cell(30, 8, f'${precio:,.2f}', 1, 0, 'R')
            pdf.cell(20, 8, str(stock), 1, 0, 'C')

            # Color según estado
            if estatus == 'disponible':
                pdf.set_text_color(0, 128, 0)  # Verde
            elif estatus == 'agotado':
                pdf.set_text_color(255, 0, 0)  # Rojo
            else:
                pdf.set_text_color(128, 128, 128)  # Gris

            pdf.cell(30, 8, estatus, 1, 1, 'C')
            pdf.set_text_color(0, 0, 0)  # Volver a negro

        return pdf

    @staticmethod
    def save_pdf_to_file(pdf, filename):
        """Guardar PDF en archivo temporal"""
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        pdf.output(filepath)
        return filepath

    @staticmethod
    def get_pdf_bytes(pdf):
        """Obtener PDF como bytes para respuesta HTTP"""
        return pdf.output(dest='S').encode('latin-1')