from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from basedatos import SessionLocal
from models.user import User
from schemas.user_schema import UserCreate, User as UserSchema  
import uuid
from pydantic import ValidationError

# Creamos el Blueprint
user_bp = Blueprint("users", __name__, url_prefix="/users")

# ---------------------------
# Función para abrir sesión DB
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
#       CREAR USUARIO
# ---------------------------

@user_bp.route("/", methods=["POST"])
def create_user():
    db = next(get_db())
    try:
        # Validamos los datos recibidos usando Pydantic
        data = request.get_json()
        user_data = UserCreate(**data)  # ⬅️ Validamos aquí

        new_user = User(
            id=str(uuid.uuid4()),
            nombre=user_data.nombre,
            rol=user_data.rol,
            especializacion=user_data.especializacion,
            horas_semanales=user_data.horas_semanales,
            dias_vacaciones=user_data.dias_vacaciones,
            historico_tiempos=user_data.historico_tiempos,
            carga_actual=user_data.carga_actual,
            riesgo_burnout=user_data.riesgo_burnout
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return jsonify({
            "message": "Usuario creado correctamente",
            "user_id": new_user.id
        })

    except ValidationError as e:
        return jsonify(e.errors()), 400

# ---------------------------
#       LISTAR USUARIOS
# ---------------------------

@user_bp.route("/", methods=["GET"])
def get_all_users():
    db = next(get_db())
    users = db.query(User).all()

    result = []
    for user in users:
        result.append({
            "id": user.id,
            "nombre": user.nombre,
            "rol": user.rol,
            "especializacion": user.especializacion,
            "horas_semanales": user.horas_semanales,
            "carga_actual": user.carga_actual,
            "riesgo_burnout": user.riesgo_burnout
        })

    return jsonify(result)
