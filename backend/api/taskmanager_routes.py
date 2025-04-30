from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from basedatos import SessionLocal
from models.task import Task
from models.client import Client
from models.alert import Alert
from models.suggestion import Suggestion
import uuid
from datetime import datetime,timedelta
from services.task_replanner import replanify_all

# Creamos el Blueprint
taskmanager_bp = Blueprint("taskmanager", __name__, url_prefix="/taskmanager")

# ---------------------------
#  Función para abrir sesión DB
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
#        TAREAS
# ---------------------------

@taskmanager_bp.route("/tasks/", methods=["POST"])
def create_task():
    data = request.get_json()
    db = next(get_db())
    new_task = Task(
        id=str(uuid.uuid4()),
        titulo=data.get("titulo"),
        descripcion=data.get("descripcion"),
        tipo=data.get("tipo"),
        prioridad=data.get("prioridad"),
        deadline=datetime.fromisoformat(data.get("deadline")),
        estimacion_horas=data.get("estimacion_horas"),
        asignado_a=data.get("asignado_a"),
        estado=data.get("estado", "No empezada"),
        revision_obligatoria=data.get("revision_obligatoria", False),
        cliente_asociado=data.get("cliente_asociado"),
        flexible=data.get("flexible", True),
        sugerencia_actual=data.get("sugerencia_actual"),
        dependencias=data.get("dependencias")
    )
    db.add(new_task)
    db.commit()
    return jsonify({"message": "Tarea creada correctamente", "task_id": new_task.id})

@taskmanager_bp.route("/tasks/", methods=["GET"])
def get_all_tasks():
    db = next(get_db())
    tasks = db.query(Task).all()
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "titulo": task.titulo,
            "descripcion": task.descripcion,
            "tipo": task.tipo,
            "prioridad": task.prioridad,
            "deadline": task.deadline.isoformat(),
            "estimacion_horas": task.estimacion_horas,
            "asignado_a": task.asignado_a,
            "estado": task.estado,
            "revision_obligatoria": task.revision_obligatoria,
            "cliente_asociado": task.cliente_asociado,
            "flexible": task.flexible,
            "sugerencia_actual": task.sugerencia_actual,
            "dependencias": task.dependencias
        })
    return jsonify(result)

@taskmanager_bp.route("/tasks/user/<string:user_id>", methods=["GET"])
def get_tasks_by_user(user_id):
    db = next(get_db())
    tasks = db.query(Task).filter(Task.asignado_a == user_id).all()
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "titulo": task.titulo,
            "descripcion": task.descripcion,
            "tipo": task.tipo,
            "prioridad": task.prioridad,
            "deadline": task.deadline.isoformat(),
            "estimacion_horas": task.estimacion_horas,
            "asignado_a": task.asignado_a,
            "estado": task.estado,
            "revision_obligatoria": task.revision_obligatoria,
            "cliente_asociado": task.cliente_asociado,
            "flexible": task.flexible,
            "sugerencia_actual": task.sugerencia_actual,
            "dependencias": task.dependencias
        })
    return jsonify(result)

@taskmanager_bp.route("/tasks/<string:task_id>", methods=["PATCH"])
def update_task(task_id):
    db = next(get_db())
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404

    data = request.get_json()



    # --- CONTROLAR DEPENDENCIAS ---
    nuevo_estado = data.get("estado")
    if nuevo_estado in ["En curso", "Terminada"]:
        if task.dependencias:
            dependencias_ids = task.dependencias.split(",")
            dependencias_no_completadas = []

            for dependencia_id in dependencias_ids:
                dependencia = db.query(Task).filter(Task.id == dependencia_id.strip()).first()
                if dependencia and dependencia.estado != "Terminada":
                    dependencias_no_completadas.append(dependencia_id.strip())

            if dependencias_no_completadas:
                return jsonify({
                    "error": "No se puede cambiar el estado.",
                    "motivo": "Hay tareas dependientes que aún no están terminadas.",
                    "dependencias_pendientes": dependencias_no_completadas
                }), 400

    # --- ACTUALIZAR CAMPOS NORMALES ---
    deadline_cambiado = False
    nueva_fecha_deadline = None

    for key, value in data.items():
        if hasattr(task, key):
            if key == "deadline" and isinstance(value, str):
                nueva_fecha_deadline = datetime.fromisoformat(value)
                setattr(task, key, nueva_fecha_deadline)
                deadline_cambiado = True
            else:
                setattr(task, key, value)

    db.commit()

    # --- ACTUALIZAR FECHAS EN CASCADA ---
    if deadline_cambiado:
        # Buscar todas las tareas que dependan de esta
        tareas_dependientes = db.query(Task).filter(Task.dependencias.like(f"%{task.id}%")).all()
        for dependiente in tareas_dependientes:
            # Si la nueva fecha límite de la tarea dependiente es anterior a la de esta tarea + 1 día, la cambiamos
            if dependiente.deadline <= nueva_fecha_deadline:
                dependiente.deadline = nueva_fecha_deadline + timedelta(days=1)
        db.commit()

    return jsonify({"message": "Tarea actualizada correctamente", "task_id": task.id})


from flask import Blueprint, request, jsonify
from models import Task, User, db
import random

taskmanager_bp = Blueprint("taskmanager", __name__, url_prefix="/taskmanager")

# Lógica de asignación dinámica de tareas
@taskmanager_bp.route("/assign-tasks", methods=["POST"])
def assign_tasks():
    tasks = db.session.query(Task).filter(Task.estado == "No empezada").all()
    users = db.session.query(User).all()
    
    # Crear un diccionario de carga de trabajo por usuario
    workload = {user.id: 0 for user in users}

    # Calcular la carga de trabajo actual de los usuarios
    for task in tasks:
        workload[task.asignado_a] += task.estimacion_horas

    # Asignar tareas a los usuarios con menos carga de trabajo
    for task in tasks:
        if task.asignado_a is None:  # Si la tarea no tiene asignado a nadie
            # Filtrar los usuarios con la especialización adecuada para la tarea
            eligible_users = [user for user in users if user.especializacion == task.tipo]

            # Encontrar el usuario con menos carga de trabajo
            user_with_least_workload = min(eligible_users, key=lambda user: workload[user.id])

            task.asignado_a = user_with_least_workload.id
            workload[user_with_least_workload.id] += task.estimacion_horas

    db.session.commit()
    return jsonify({"message": "Tareas asignadas correctamente."}), 200

# ---------------------------
#        CLIENTES
# ---------------------------

@taskmanager_bp.route("/clients/", methods=["POST"])
def create_client():
    data = request.get_json()
    db = next(get_db())
    new_client = Client(
        id=str(uuid.uuid4()),
        nombre=data.get("nombre"),
        facturacion_total=data.get("facturacion_total", 0.0),
        importancia_estrategica=data.get("importancia_estrategica", "Media"),
        relaciones=data.get("relaciones")
    )
    db.add(new_client)
    db.commit()
    return jsonify({"message": "Cliente creado correctamente", "client_id": new_client.id})

@taskmanager_bp.route("/clients/", methods=["GET"])
def get_all_clients():
    db = next(get_db())
    clients = db.query(Client).all()
    result = []
    for client in clients:
        result.append({
            "id": client.id,
            "nombre": client.nombre,
            "facturacion_total": client.facturacion_total,
            "importancia_estrategica": client.importancia_estrategica,
            "relaciones": client.relaciones
        })
    return jsonify(result)

# ---------------------------
#        ALERTAS
# ---------------------------

@taskmanager_bp.route("/alerts/", methods=["POST"])
def create_alert():
    data = request.get_json()
    db = next(get_db())
    new_alert = Alert(
        id=str(uuid.uuid4()),
        tipo=data.get("tipo"),
        mensaje=data.get("mensaje"),
        usuario_afectado=data.get("usuario_afectado"),
        tarea_afectada=data.get("tarea_afectada"),
        fecha_generacion=datetime.now()  # Lo generamos automáticamente al crear
    )
    db.add(new_alert)
    db.commit()
    return jsonify({"message": "Alerta creada correctamente", "alert_id": new_alert.id})

@taskmanager_bp.route("/alerts/", methods=["GET"])
def get_all_alerts():
    db = next(get_db())
    alerts = db.query(Alert).all()
    result = []
    for alert in alerts:
        result.append({
            "id": alert.id,
            "tipo": alert.tipo,
            "mensaje": alert.mensaje,
            "usuario_afectado": alert.usuario_afectado,
            "tarea_afectada": alert.tarea_afectada,
            "fecha_generacion": alert.fecha_generacion.isoformat()
        })
    return jsonify(result)

# ---------------------------
#       SUGERENCIAS
# ---------------------------

@taskmanager_bp.route("/suggestions/", methods=["POST"])
def create_suggestion():
    data = request.get_json()
    db = next(get_db())
    new_suggestion = Suggestion(
        id=str(uuid.uuid4()),
        tarea_sugerida=data.get("tarea_sugerida"),
        usuario_actual=data.get("usuario_actual"),
        usuario_recomendado=data.get("usuario_recomendado"),
        motivo=data.get("motivo"),
        aceptada=None  # Por defecto la sugerencia está pendiente
    )
    db.add(new_suggestion)
    db.commit()
    return jsonify({"message": "Sugerencia creada correctamente", "suggestion_id": new_suggestion.id})

@taskmanager_bp.route("/suggestions/", methods=["GET"])
def get_all_suggestions():
    db = next(get_db())
    suggestions = db.query(Suggestion).all()
    result = []
    for suggestion in suggestions:
        result.append({
            "id": suggestion.id,
            "tarea_sugerida": suggestion.tarea_sugerida,
            "usuario_actual": suggestion.usuario_actual,
            "usuario_recomendado": suggestion.usuario_recomendado,
            "motivo": suggestion.motivo,
            "aceptada": suggestion.aceptada
        })
    return jsonify(result)

@taskmanager_bp.route("/suggestions/<string:suggestion_id>", methods=["PATCH"])
def update_suggestion(suggestion_id):
    db = next(get_db())
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not suggestion:
        return jsonify({"error": "Sugerencia no encontrada"}), 404

    data = request.get_json()
    aceptada = data.get("aceptada")
    if aceptada not in [True, False]:
        return jsonify({"error": "Campo 'aceptada' debe ser true o false."}), 400

    suggestion.aceptada = aceptada
    db.commit()
    return jsonify({"message": "Sugerencia actualizada correctamente", "suggestion_id": suggestion.id})

@taskmanager_bp.route("/replanify", methods=["POST"])
def trigger_replanification():
    replanify_all()
    return jsonify({"message": "Replanificación ejecutada. Se han creado sugerencias y alertas si era necesario."})