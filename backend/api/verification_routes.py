from flask import Blueprint, request, jsonify
from models.verification import verify_contract_data
from utils.error_handler import handle_exceptions

# Creamos el Blueprint para las rutas de verificación
data_verification_bp = Blueprint('data_verification', __name__)


@data_verification_bp.route('/verifyContractData', methods=['POST'])
@handle_exceptions
def verify_contract():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibió contenido JSON"}), 400

    contract_text = data.get("contract_text", "").strip()
    if not contract_text:
        return jsonify({"error": "No se recibió texto válido del contrato"}), 400

    # Llama a la función que gestiona la verificación semántica
    issues = verify_contract_data(contract_text)

    return jsonify({"issues": issues}), 200
