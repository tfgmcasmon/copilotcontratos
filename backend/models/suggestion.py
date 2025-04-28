from sqlalchemy import Column, String, Boolean
from basedatos import Base

class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(String, primary_key=True, index=True)
    tarea_sugerida = Column(String, nullable=False)  # ID de la tarea
    usuario_actual = Column(String, nullable=False)  # ID del usuario asignado actualmente
    usuario_recomendado = Column(String, nullable=False)  # ID del usuario recomendado
    motivo = Column(String, nullable=False)  # Sobrecarga / Cambio de fecha / Optimización de carga
    aceptada = Column(Boolean, default=None)  # None = pendiente, True = aceptada, False = rechazada
