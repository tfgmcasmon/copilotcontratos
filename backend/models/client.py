from sqlalchemy import Column, String, Float
from basedatos import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    facturacion_total = Column(Float, default=0.0)
    importancia_estrategica = Column(String, default="Media")  # Alta, Media, Baja
    relaciones = Column(String)  # IDs de otros clientes relacionados, separados por comas
