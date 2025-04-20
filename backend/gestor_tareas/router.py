# backend/gestor_tareas/router.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from .models import Tarea, Usuario  # Asegúrate de que estas clases estén definidas en models.py
from .logic import asignar_tarea_automatica
from .utils import TAREAS_ACTIVAS, agregar_tarea_desde_dict, USUARIOS_FAKE
from .llm_routing import analizar_tarea_con_llm



gestor_tareas_bp = Blueprint("gestor_tareas", __name__)

@gestor_tareas_bp.route("/asignaciones", methods=["GET"])
def obtener_tareas_asignadas():
    resultados = []
    for tarea in TAREAS_ACTIVAS:
        asignada = asignar_tarea_automatica(tarea, USUARIOS_FAKE)
        for subtarea in asignada.subtareas:
            responsable = subtarea.responsable
            resultados.append({
                "tarea_id": tarea.id,
                "titulo": tarea.titulo,
                "tipo": tarea.tipo,
                "cliente": tarea.cliente,
                "urgencia": tarea.urgencia,
                "fecha_limite": tarea.fecha_limite.strftime("%Y-%m-%d") if tarea.fecha_limite else None,
                "asignado": responsable.nombre if responsable else None,
                "rol": responsable.rol if responsable else None,
                "fecha_sugerida": subtarea.fecha_sugerida if hasattr(subtarea, "fecha_sugerida") else None,
                "fecha_inicio": None,
                "fecha_fin": None
            })
    return jsonify({"asignaciones": resultados})

@gestor_tareas_bp.route("/nueva", methods=["POST"])
def crear_tarea():
    try:
        data = request.get_json()
        print("📩 Datos recibidos:", data)

        nueva = Tarea(
            id=len(TAREAS_ACTIVAS) + 1,
            titulo=data["titulo"],
            tipo=data["tipo"],
            cliente=data["cliente"],
            urgencia=data["urgencia"],
            fecha_limite=data["fecha_limite"]
        )

        tarea_asignada = asignar_tarea_automatica(nueva, USUARIOS_FAKE)
        TAREAS_ACTIVAS.append(tarea_asignada)

        subtareas = [
            {
                "descripcion": st.descripcion,
                "responsable": st.responsable.nombre if st.responsable else "Sin asignar",
                "rol": st.responsable.rol if st.responsable else "N/A"
            } for st in tarea_asignada.subtareas
        ]

        return jsonify({
            "resultado": {
                "tarea_id": tarea_asignada.id,
                "titulo": tarea_asignada.titulo,
                "cliente": tarea_asignada.cliente,
                "urgencia": tarea_asignada.urgencia,
                "fecha_limite": tarea_asignada.fecha_limite,
                "subtareas": subtareas
            }
        })

    except Exception as e:
        print("❌ Error en /nueva:", e)
        return jsonify({"error": "Fallo al crear tarea"}), 500
