from datetime import datetime, timedelta
from gestor_tareas.models import Tarea, Subtarea, Usuario


FASES_TAREA = {
    "redaccion": ["junior", "intermedio"],
    "traduccion": ["intermedio"],
    "firma": ["socia"],
    "compraventa inmueble": ["junior", "intermedio", "socia"],
    "due diligence": ["junior", "intermedio"]
}

def generar_subtareas_por_tipo(tipo_tarea):
    subtareas = []
    if tipo_tarea == "firma":
        subtareas = [
            Subtarea("Revisar documentos finales", bloquea=True),
            Subtarea("Reunión con cliente para firma", bloquea=True),
            Subtarea("Cierre y archivo de documentos"),
        ]
    elif tipo_tarea == "compraventa inmueble":
        subtareas = [
            Subtarea("Redacción del contrato"),
            Subtarea("Revisión del contrato por el socio"),
            Subtarea("Traducción si procede"),
            #solicitud de revision de registros publicos---lo hace el junior o una secretaria
            Subtarea("Firma en notaría", bloquea=True)
        ]
    elif tipo_tarea == "due diligence": #auditoria
        subtareas = [
            Subtarea("Asignar revisión documental a junior"),
            Subtarea("Revisión de cláusulas sensibles"),
            #asignacion de limitacion de riesgos para el desarrollo de la operacion
            #redaccion del informe
            Subtarea("Reunión con cliente para análisis de riesgos")
        ]
    else:
        subtareas = [Subtarea("Paso inicial genérico"), Subtarea("Paso final")]
    return subtareas

def calcular_carga(usuario: Usuario):
    base = len(usuario.tareas_asignadas)
    if usuario.rol == "becario":
        return base * 2
    elif usuario.rol == "junior":
        return base * 1.5
    #asociado
    #asociado senior 
    elif usuario.rol == "intermedio":
        return base * 1.2
    return base

def disponibilidad(usuario, fecha):
    bloqueos = getattr(usuario, "bloqueos", [])
    return fecha.strftime("%Y-%m-%d") not in bloqueos

def calcular_prioridad(usuario, tarea, fecha_base):
    penalizacion_carga = usuario.carga
    urgencia_factor = {"alta": 1.0, "media": 1.5, "baja": 2.0}.get(tarea.urgencia, 1.5)
    rol_penalty = {"socia": 3, "intermedio": 1.2, "junior": 1.5}.get(usuario.rol, 1.0)

    # Asegura que fecha_limite sea datetime
    if isinstance(tarea.fecha_limite, str):
        fecha_limite_dt = datetime.strptime(tarea.fecha_limite, "%Y-%m-%d")
    else:
        fecha_limite_dt = tarea.fecha_limite

    dias_hasta_limite = (tarea.fecha_limite - fecha_base).days
    return penalizacion_carga * rol_penalty * urgencia_factor - dias_hasta_limite


def seleccionar_mejor_usuario(usuarios, tarea):
    fecha_base = datetime.today()
    candidatos = [u for u in usuarios if u.rol in FASES_TAREA.get(tarea.tipo, [])]
    puntuaciones = [(usuario, calcular_prioridad(usuario, tarea, fecha_base)) for usuario in candidatos if disponibilidad(usuario, fecha_base)]
    puntuaciones.sort(key=lambda x: x[1])
    return puntuaciones[0][0] if puntuaciones else None

def asignar_tarea_automatica(tarea: Tarea, usuarios: list):
    tarea.subtareas = generar_subtareas_por_tipo(tarea.tipo)
    for subtarea in tarea.subtareas:
        responsable = seleccionar_mejor_usuario(usuarios, tarea)
        subtarea.responsable = responsable
        if responsable:
            responsable.tareas_asignadas.append(subtarea)
    return tarea
