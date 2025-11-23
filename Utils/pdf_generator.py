from fpdf import FPDF
from datetime import datetime
import os
import json


class ParnetPDF(FPDF):
    """Clase personalizada para generar PDFs en Parnet Ingeniería"""

    def header(self):
        # Logo
        self.image('static/images/logo.png', 10, 8, 33)
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
        pdf.cell(0, 10, product.nombre, 0, 1)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'SKU:', 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, product.sku, 0, 1)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'Precio:', 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'${float(product.precio):,.2f} MXN', 0, 1)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'Stock:', 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, str(product.stock), 0, 1)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'Estado:', 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, product.get_estatus_display(), 0, 1)
        pdf.ln(10)

        # Descripción
        if product.descripcion_larga:
            pdf.chapter_title('DESCRIPCIÓN')
            pdf.multi_cell(0, 10, product.descripcion_larga)
            pdf.ln(10)

        # Especificaciones
        if product.especificaciones:
            pdf.chapter_title('ESPECIFICACIONES TÉCNICAS')
            pdf.multi_cell(0, 10, product.especificaciones)
            pdf.ln(10)

        # Características
        if product.caracteristicas:
            try:
                características = product.caracteristicas
                if isinstance(características, str):
                    características = json.loads(características)

                pdf.chapter_title('CARACTERÍSTICAS')
                for key, value in características.items():
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(50, 8, f'{key}:', 0, 0)
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 8, str(value), 0, 1)
            except:
                # Si hay error al parsear JSON, mostrar como texto
                pdf.multi_cell(0, 10, str(product.caracteristicas))

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
            pdf.cell(0, 8, sugerencia.nombre, 0, 1)

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Email:', 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, sugerencia.email, 0, 1)

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Asunto:', 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, sugerencia.asunto or 'Sin asunto', 0, 1)

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Fecha:', 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, sugerencia.fecha_creacion.strftime("%d/%m/%Y %H:%M"), 0, 1)

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Mensaje:', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 8, sugerencia.mensaje)

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
        disponibles = len([p for p in products if p.estatus == 'disponible'])
        agotados = len([p for p in products if p.estatus == 'agotado'])

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
            nombre = producto.nombre[:35] + '...' if len(producto.nombre) > 35 else producto.nombre
            pdf.cell(80, 8, nombre, 1, 0)
            pdf.cell(30, 8, producto.sku, 1, 0, 'C')
            pdf.cell(30, 8, f'${float(producto.precio or 0):,.2f}', 1, 0, 'R')
            pdf.cell(20, 8, str(producto.stock), 1, 0, 'C')

            # Color según estado
            if producto.estatus == 'disponible':
                pdf.set_text_color(0, 128, 0)  # Verde
            elif producto.estatus == 'agotado':
                pdf.set_text_color(255, 0, 0)  # Rojo
            else:
                pdf.set_text_color(128, 128, 128)  # Gris

            pdf.cell(30, 8, producto.get_estatus_display(), 1, 1, 'C')
            pdf.set_text_color(0, 0, 0)  # Volver a negro

        return pdf

    @staticmethod
    def save_pdf_to_file(pdf, filename):
        """Guardar PDF en archivo temporal"""
        import tempfile
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        pdf.output(filepath)
        return filepath

    @staticmethod
    def get_pdf_bytes(pdf):
        """Obtener PDF como bytes para respuesta HTTP"""
        return pdf.output(dest='S').encode('latin-1')