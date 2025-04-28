from sqlalchemy import Column, String, Integer, Boolean, JSON
from basedatos import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    rol = Column(String, nullable=False)  # Socio, Asociado, Junior, Becario
    especializacion = Column(String, nullable=False)  # Mercantil, Inmobiliario, Otros
    horas_semanales = Column(Integer, nullable=False)
    dias_vacaciones = Column(JSON)  # Lista de fechas bloqueadas
    historico_tiempos = Column(JSON)  # Tipo de tarea → horas medias
    carga_actual = Column(Integer, default=0)
    riesgo_burnout = Column(Boolean, default=False)
