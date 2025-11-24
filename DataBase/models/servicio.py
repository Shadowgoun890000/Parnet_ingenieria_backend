from . import db, BaseModel


class Servicio(BaseModel):
    __tablename__ = 'servicios'

    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    area = db.Column(db.String(50), nullable=False)  # telecomunicaciones, software, energía, consultoría
    caracteristicas = db.Column(db.JSON)  # Lista de características del servicio
    orden = db.Column(db.Integer, default=0)

    # Relación con solicitudes
    solicitudes = db.relationship('SolicitudServicio', backref='servicio', lazy=True)

    def to_dict(self):
        data = super().to_dict()
        data['total_solicitudes'] = len(self.solicitudes)
        return data


class SolicitudServicio(BaseModel):
    __tablename__ = 'solicitudes_servicios'

    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    empresa = db.Column(db.String(100))
    mensaje = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, en_proceso, atendido

    def __repr__(self):
        return f'<SolicitudServicio {self.nombre_cliente}>'