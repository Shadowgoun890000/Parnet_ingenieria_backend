from . import db, BaseModel


class Contacto(BaseModel):
    __tablename__ = 'contactos'

    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    asunto = db.Column(db.String(200))
    mensaje = db.Column(db.Text, nullable=False)
    respondido = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Contacto {self.nombre}>'


class Sugerencia(BaseModel):
    __tablename__ = 'sugerencias'

    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    asunto = db.Column(db.String(200))
    mensaje = db.Column(db.Text, nullable=False)
    leida = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Sugerencia {self.nombre}>'