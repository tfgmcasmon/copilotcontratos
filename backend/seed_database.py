from basedatos import SessionLocal, engine, Base
from models.user import User
from models.task import Task
import uuid
from datetime import datetime, timedelta
import random

# Crea la base de datos si no existe
Base.metadata.create_all(bind=engine)

# Usuarios de prueba
usuarios_fake = [
    {"nombre": "María Pérez", "rol": "Asociado", "especializacion": "Mercantil", "horas_semanales": 40},
    {"nombre": "Luis García", "rol": "Junior", "especializacion": "Inmobiliario", "horas_semanales": 35},
    {"nombre": "Ana López", "rol": "Becario", "especializacion": "Mercantil", "horas_semanales": 30},
    {"nombre": "Carlos Ruiz", "rol": "Socio", "especializacion": "Inmobiliario", "horas_semanales": 45}
]

# Títulos de tareas aleatorias
# Tareas de ejemplo
tareas_fake = [
    {"titulo": "Preparar contrato de arras", "tipo": "Redacción", "prioridad": "Alta", "estado": "No empezada"},
    {"titulo": "Revisión escritura pública", "tipo": "Revisión", "prioridad": "Media", "estado": "No empezada"},
    {"titulo": "Redactar informe de due diligence", "tipo": "Redacción", "prioridad": "Baja", "estado": "En curso"},
    {"titulo": "Elaborar contrato de compraventa", "tipo": "Redacción", "prioridad": "Alta", "estado": "No empezada"},
]


def seed_database():
    db = SessionLocal()

    # Limpiar datos antiguos (opcional, solo si quieres hacerlo seguro)
    db.query(Task).delete()
    db.query(User).delete()
    db.commit()

    # Insertar usuarios
    users_created = []
    for usuario in usuarios_fake:
        new_user = User(
            id=str(uuid.uuid4()),
            nombre=usuario["nombre"],
            rol=usuario["rol"],
            especializacion=usuario["especializacion"],
            horas_semanales=usuario["horas_semanales"],
            dias_vacaciones=[],
            historico_tiempos={},
            carga_actual=0,
            riesgo_burnout=False
        )
        db.add(new_user)
        users_created.append(new_user)

    db.commit()

   # Insertar tareas aleatorias con fecha y prioridad
    for tarea_data in tareas_fake:
        # Generar fechas y prioridades aleatorias
        deadline = datetime.now() + timedelta(days=random.randint(1, 10))
        prioridad = random.choice(["Alta", "Media", "Baja"])
        assigned_user = random.choice(users_created).id  # Asignar aleatoriamente a un usuario

        nueva_tarea = Task(
            id=str(uuid.uuid4()),
            titulo=tarea_data["titulo"],  # Aquí es donde accedemos al diccionario
            descripcion="Descripción generada automáticamente.",
            tipo=tarea_data["tipo"],
            prioridad=prioridad,
            deadline=deadline,
            estimacion_horas=random.randint(2, 8),
            asignado_a=assigned_user,
            estado=tarea_data["estado"],
            revision_obligatoria=random.choice([True, False]),
            cliente_asociado=None,
            flexible=True,
            sugerencia_actual=None,
            dependencias=""
        )
        db.add(nueva_tarea)


    db.commit()
    db.close()
    print("¡Base de datos rellenada con datos de prueba!")

if __name__ == "__main__":
    seed_database()