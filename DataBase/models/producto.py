from . import db, BaseModel


class CategoriaProducto(BaseModel):
    __tablename__ = 'categorias_productos'

    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    orden = db.Column(db.Integer, default=0)

    # Relación con productos
    productos = db.relationship('Producto', backref='categoria', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        data = super().to_dict()
        data['total_productos'] = len(self.productos)
        return data


class Producto(BaseModel):
    __tablename__ = 'productos'

    nombre = db.Column(db.String(150), nullable=False)
    descripcion_corta = db.Column(db.String(255))
    descripcion_larga = db.Column(db.Text)
    especificaciones = db.Column(db.Text)  # JSON string con especificaciones
    precio = db.Column(db.Numeric(10, 2))
    imagen_principal = db.Column(db.String(255))
    imagenes_adicionales = db.Column(db.JSON)  # Lista de URLs de imágenes
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_productos.id'), nullable=False)
    stock = db.Column(db.Integer, default=0)
    estatus = db.Column(db.String(20), default='disponible')  # disponible, agotado, descontinuado
    destacado = db.Column(db.Boolean, default=False)
    sku = db.Column(db.String(50), unique=True)  # Código único del producto
    caracteristicas = db.Column(db.JSON)  # Características en formato clave-valor

    def get_estatus_display(self):
        """Obtener texto descriptivo del estatus"""
        estatus_map = {
            'disponible': 'En Existencia',
            'agotado': 'Agotado',
            'descontinuado': 'Descontinuado'
        }
        return estatus_map.get(self.estatus, self.estatus)

    def to_dict(self):
        data = super().to_dict()
        # Convertir decimal a float para JSON
        if data.get('precio'):
            data['precio'] = float(data['precio'])
        data['estatus_display'] = self.get_estatus_display()
        return data

    def __repr__(self):
        return f'<Producto {self.nombre}>'
