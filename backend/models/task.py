from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from models.client import Client
from models.user import User
from basedatos import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String)
    tipo = Column(String, nullable=False)  # Informe, Revisión, Firma, Comunicación, etc.
    prioridad = Column(String, nullable=False)  # Alta, Media, Baja
    deadline = Column(DateTime, nullable=False)
    estimacion_horas = Column(Float, nullable=False)
    asignado_a = Column(String, ForeignKey('users.id'))  # usuario actual
    estado = Column(String, default="No empezada")  # No empezada / En curso / Terminada
    revision_obligatoria = Column(Boolean, default=False)
    cliente_asociado = Column(String, ForeignKey('clients.id'))
    flexible = Column(Boolean, default=True)  # ¿Puede reasignarse si no empezada?
    sugerencia_actual = Column(String, ForeignKey('users.id'), nullable=True)  # usuario recomendado si se sugiere cambio

    dependencias = Column(String)  # lista de ids de tareas anteriores como string separado por comas (simple)
