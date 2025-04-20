from datetime import datetime
from .models import Tarea
from .models import Usuario

USUARIOS_FAKE = [
    Usuario(nombre="Laura S.", rol="socia", carga=12, bloqueos=["2025-04-22"]),
    Usuario(nombre="Mario G.", rol="junior", carga=6, bloqueos=["2025-04-25"]),
    Usuario(nombre="Clara T.", rol="intermedio", carga=9, bloqueos=["2025-04-21", "2025-04-22"]),
    Usuario(nombre="Andrés B.", rol="junior", carga=3, bloqueos=[]),
]

TAREAS_ACTIVAS = []

# backend/gestor_tareas/utils.py (actualiza agregar_tarea_desde_dict)
def agregar_tarea_desde_dict(datos_dict):
    nueva_tarea = Tarea(
        id=len(TAREAS_ACTIVAS) + 1,
        titulo=datos_dict.get("titulo", ""),
        tipo=datos_dict.get("tipo", ""),
        cliente=datos_dict.get("cliente", ""),
        descripcion=datos_dict.get("descripcion", ""),  # 👈 nuevo campo
        urgencia=datos_dict.get("urgencia", "media"),
        fecha_limite=datetime.strptime(datos_dict.get("fecha_limite"), "%Y-%m-%d") if datos_dict.get("fecha_limite") else None
    )
    TAREAS_ACTIVAS.append(nueva_tarea)
    return nueva_tarea

