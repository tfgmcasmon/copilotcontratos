from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    tipo: str
    prioridad: str
    deadline: datetime
    estimacion_horas: float
    asignado_a: Optional[str] = None
    estado: Optional[str] = "No empezada"
    revision_obligatoria: Optional[bool] = False
    cliente_asociado: Optional[str] = None
    flexible: Optional[bool] = True
    sugerencia_actual: Optional[str] = None
    dependencias: Optional[str] = None  # Lista de IDs separados por comas

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str

    class Config:
        orm_mode = True
