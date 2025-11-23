from . import db, BaseModel

class Cliente(BaseModel):
    __tablename__="clientes"

    nombre_empresa=db.Column(db.String(150), nullable=False)
    logo = db.Column(db.String(255))
    enlace_web = db.Column(db.String(255))
    testimonio = db.Column(db.Text)
    orden =db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Cliente {self.nombre_empresa}"