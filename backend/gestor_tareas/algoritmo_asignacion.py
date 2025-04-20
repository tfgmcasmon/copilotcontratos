# backend/algoritmo_asignacion.py

from datetime import datetime, timedelta
import random

# Simulación de estructura de datos: tareas y abogados
TAREAS_FAKE = [
    {
        "id": 1,
        "titulo": "Redactar contrato arrendamiento local comercial",
        "tipo": "redaccion",
        "cliente": "Grupo Realia",
        "urgencia": "alta",
        "estimado_horas": 6,
        "fecha_limite": "2025-04-20",
    },
    {
        "id": 2,
        "titulo": "Traducción contrato compraventa internacional",
        "tipo": "traduccion",
        "cliente": "Inversiones Global S.A.",
        "urgencia": "media",
        "estimado_horas": 3,
        "fecha_limite": "2025-04-25",
    },
    {
        "id": 3,
        "titulo": "Firma notarial escritura hotel",
        "tipo": "firma",
        "cliente": "Hotel Mirasierra",
        "urgencia": "alta",
        "estimado_horas": 2,
        "fecha_limite": "2025-04-18",
    },
]

ABOGADOS_FAKE = [
    {"id": 1, "nombre": "Laura S.", "rol": "socia", "carga_actual": 15, "disponibilidad": ["2025-04-17", "2025-04-18", "2025-04-21"]},
    {"id": 2, "nombre": "Mario G.", "rol": "junior", "carga_actual": 6, "disponibilidad": ["2025-04-17", "2025-04-18", "2025-04-22"]},
    {"id": 3, "nombre": "Clara T.", "rol": "intermedio", "carga_actual": 10, "disponibilidad": ["2025-04-18", "2025-04-19", "2025-04-20"]},
]

# Lógica simplificada para asignar tareas

FASES_TAREA = {
    "redaccion": ["junior", "intermedio"],
    "traduccion": ["intermedio"],
    "firma": ["socia"]
}

def asignar_tarea(tarea, abogados):
    elegibles = [a for a in abogados if a["rol"] in FASES_TAREA[tarea["tipo"]]]

    # Ordenamos por carga de trabajo
    ordenados = sorted(elegibles, key=lambda x: x["carga_actual"])
    if not ordenados:
        return None

    asignado = ordenados[0]
    return {
        "tarea_id": tarea["id"],
        "asignado": asignado["nombre"],
        "fecha_sugerida": sugerir_fecha(asignado["disponibilidad"], tarea["fecha_limite"]),
        "rol": asignado["rol"]
    }

def sugerir_fecha(disponibilidad, fecha_limite):
    try:
        fechas_ordenadas = sorted(disponibilidad)
        for fecha in fechas_ordenadas:
            if fecha <= fecha_limite:
                return fecha
    except:
        pass
    return fecha_limite

# Prueba general
if __name__ == "__main__":
    print("\n📌 RESULTADOS DE ASIGNACIÓN:\n")
    for tarea in TAREAS_FAKE:
        resultado = asignar_tarea(tarea, ABOGADOS_FAKE)
        print(f"📝 {tarea['titulo']} → Asignado a: {resultado['asignado']} ({resultado['rol']}) el día {resultado['fecha_sugerida']}")
