from . import db, BaseModel


class Noticia(BaseModel):
    __tablename__ = 'noticias'

    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    resumen = db.Column(db.String(500))
    imagen = db.Column(db.String(255))
    autor = db.Column(db.String(100))
    fecha_publicacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    visitas = db.Column(db.Integer, default=0)
    etiquetas = db.Column(db.JSON)  # Lista de etiquetas

    def incrementar_visitas(self):
        """Incrementar contador de visitas"""
        self.visitas += 1
        self.save()

    def __repr__(self):
        return f'<Noticia {self.titulo}>'