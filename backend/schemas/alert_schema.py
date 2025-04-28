from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    tipo: str
    mensaje: str
    usuario_afectado: Optional[str] = None
    tarea_afectada: Optional[str] = None
    fecha_generacion: datetime

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: str

    class Config:
        orm_mode = True
