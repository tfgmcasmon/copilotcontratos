from models.task import Task
from models.user import User
from models.suggestion import Suggestion
from models.alert import Alert
from basedatos import SessionLocal
import uuid
from datetime import datetime, timedelta

# ---------------------------
# FUNCIÓN 1: Verificar sobrecarga de usuarios
# ---------------------------

def check_user_overload(db, carga_maxima=40):
    """Detecta usuarios que superan su carga máxima y crea alertas si es necesario"""
    users = db.query(User).all()
    for user in users:
        if user.carga_actual > carga_maxima:
            alerta = Alert(
                id=str(uuid.uuid4()),
                tipo="Riesgo de burnout",
                mensaje=f"El usuario {user.nombre} está sobrecargado ({user.carga_actual} horas asignadas).",
                usuario_afectado=user.id,
                tarea_afectada=None,
                fecha_generacion=datetime.now()
            )
            db.add(alerta)
    db.commit()

# ---------------------------
# FUNCIÓN 2: Sugerir reasignación de tareas flexibles
# ---------------------------

def suggest_task_reassignments(db):
    """Sugiere cambios de asignación para optimizar cargas de trabajo"""
    tasks = db.query(Task).filter(Task.estado == "No empezada", Task.flexible == True).all()
    users = db.query(User).all()

    for task in tasks:
        if not task.asignado_a:
            continue

        assigned_user = db.query(User).filter(User.id == task.asignado_a).first()
        if not assigned_user:
            continue

        # Buscar un usuario mejor: menos carga y misma especialización
        better_candidates = sorted(
            (u for u in users if u.id != assigned_user.id and u.especializacion == assigned_user.especializacion),
            key=lambda x: x.carga_actual
        )

        if better_candidates and better_candidates[0].carga_actual + task.estimacion_horas < assigned_user.carga_actual:
            suggestion = Suggestion(
                id=str(uuid.uuid4()),
                tarea_sugerida=task.id,
                usuario_actual=assigned_user.id,
                usuario_recomendado=better_candidates[0].id,
                motivo="Optimización de carga de trabajo",
                aceptada=None
            )
            db.add(suggestion)

    db.commit()

# ---------------------------
# FUNCIÓN 3: Ejecutar todo junto
# ---------------------------

def replanify_all(carga_maxima=40):
    """Ejecuta verificación de sobrecarga y sugerencias inteligentes"""
    db = SessionLocal()
    try:
        check_user_overload(db, carga_maxima)
        detect_deadline_risks(db, umbral_dias=1)
        suggest_task_reassignments(db)
    finally:
        db.close()


# ---------------------------
# FUNCIÓN 4: Detectar riesgo de retraso
# ---------------------------

def detect_deadline_risks(db, umbral_dias=1):
    """Detecta tareas cuyo deadline está muy cerca y genera alertas"""
    ahora = datetime.now()
    tareas = db.query(Task).filter(Task.estado.in_(["No empezada", "En curso"])).all()

    for tarea in tareas:
        if tarea.deadline - ahora <= timedelta(days=umbral_dias):
            # Buscar si ya existe alerta para evitar duplicados
            alerta_existente = db.query(Alert).filter(Alert.tarea_afectada == tarea.id, Alert.tipo == "Riesgo de retraso").first()
            if not alerta_existente:
                alerta = Alert(
                    id=str(uuid.uuid4()),
                    tipo="Riesgo de retraso",
                    mensaje=f"La tarea '{tarea.titulo}' está a punto de vencer (deadline {tarea.deadline.date()}).",
                    usuario_afectado=tarea.asignado_a,
                    tarea_afectada=tarea.id,
                    fecha_generacion=datetime.now()
                )
                db.add(alerta)
    db.commit()
