from pydantic import BaseModel
from typing import Optional

class SuggestionBase(BaseModel):
    tarea_sugerida: str
    usuario_actual: str
    usuario_recomendado: str
    motivo: str
    aceptada: Optional[bool] = None

class SuggestionCreate(SuggestionBase):
    pass

class Suggestion(SuggestionBase):
    id: str

    class Config:
        orm_mode = True
