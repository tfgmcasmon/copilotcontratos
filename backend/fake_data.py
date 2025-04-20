# algoritmo_asignacion.py
from backend.fake_data import ABOGADOS, TAREAS
from datetime import datetime

ROL_FASE = {
    "redacción": ["junior", "intermedio"],
    "revisión": ["intermedio", "socia"],
    "firma": ["socia"]
}

def obtener_disponibles(rol, hora_bloqueo=None):
    disponibles = []
    for abogado in ABOGADOS:
        if abogado["rol"] in rol:
            if hora_bloqueo and hora_bloqueo in abogado.get("bloqueos", []):
                continue
            disponibles.append(abogado)
    return disponibles

def asignar_tareas():
    asignaciones = []
    for tarea in TAREAS:
        if not tarea["aprobado"]:
            print(f"⏳ Tarea '{tarea['titulo']}' pendiente de aprobación.")
            continue
        for fase in tarea["fases"]:
            rol_deseado = ROL_FASE.get(fase["tipo"], [])
            bloqueada = fase.get("bloqueo", False)
            hora_firma = tarea["fecha_limite"] if bloqueada else None

            disponibles = obtener_disponibles(rol_deseado, hora_firma)

            if disponibles:
                seleccionado = disponibles[0]  # por ahora, elegimos el primero
                asignaciones.append((fase["tipo"], seleccionado["nombre"]))
                print(f"✅ Fase '{fase['tipo']}' asignada a {seleccionado['nombre']}")
            else:
                print(f"❌ No hay abogados disponibles para fase '{fase['tipo']}'")
    return asignaciones
