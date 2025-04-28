from pydantic import BaseModel
from typing import Optional

class ClientBase(BaseModel):
    nombre: str
    facturacion_total: Optional[float] = 0.0
    importancia_estrategica: Optional[str] = "Media"
    relaciones: Optional[str] = None  # IDs separados por comas

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: str

    class Config:
        orm_mode = True
