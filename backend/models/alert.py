from sqlalchemy import Column, String, DateTime
from basedatos import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # Riesgo de retraso / Riesgo de burnout / etc.
    mensaje = Column(String, nullable=False)
    usuario_afectado = Column(String)  # ID de usuario afectado (opcional)
    tarea_afectada = Column(String)    # ID de tarea afectada (opcional)
    fecha_generacion = Column(DateTime, nullable=False)
