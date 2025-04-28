from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    nombre: str
    rol: str
    especializacion: str
    horas_semanales: int
    dias_vacaciones: Optional[list] = []
    historico_tiempos: Optional[dict] = {}
    carga_actual: Optional[int] = 0
    riesgo_burnout: Optional[bool] = False

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str

    class Config:
        orm_mode = True
