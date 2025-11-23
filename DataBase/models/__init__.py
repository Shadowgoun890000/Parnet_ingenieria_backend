from .database import db
from datetime import datetime


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    def save(self):
        """Guardar objeto en la base de datos"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error guardando objeto: {e}")
            return False

    def delete(self):
        """Eliminar objeto de la base de datos"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error eliminando objeto: {e}")
            return False

    def to_dict(self):
        """Convertir objeto a diccionario"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }