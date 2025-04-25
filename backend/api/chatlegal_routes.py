from flask import Blueprint, request, jsonify
from models.chat_response import generate_chat_response
from utils.error_handler import handle_exceptions

# Creamos el Blueprint para las rutas de ChatLegal
chatlegal_bp = Blueprint('chatlegal', __name__)


@chatlegal_bp.route('/askLegalQuestion', methods=['POST'])
@handle_exceptions
def ask_legal_question():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibió contenido JSON"}), 400

    question = data.get('question', '').strip()
    if not question:
        return jsonify({"error": "No se recibió pregunta válida"}), 400

    # Llama a la función que genera la respuesta legal
    answer = generate_chat_response(question)

    return jsonify({"answer": answer}), 200
