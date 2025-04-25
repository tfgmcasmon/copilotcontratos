from flask import Blueprint, jsonify

# Creamos el Blueprint para la ruta de healthcheck
healthcheck_bp = Blueprint('healthcheck', __name__)

@healthcheck_bp.route('/ping', methods=['GET'])
def ping():
    """
    Endpoint simple para comprobar que el servidor está vivo.
    """
    return jsonify({"status": "ok", "message": "pong"}), 200
