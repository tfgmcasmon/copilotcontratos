# backend/api/legalchat_routes.py

from flask import Blueprint, request, jsonify
from utils.error_handler import handle_exceptions
from models.legalchat import generate_legal_chat_response

legalchat_bp = Blueprint('legalchat', __name__)

@legalchat_bp.route('/legalChat', methods=['POST'])
@handle_exceptions
def legal_chat():
    data = request.get_json()
    messages = data.get("messages", [])

    if not messages or not isinstance(messages, list):
        return jsonify({"error": "Formato de mensajes inválido"}), 400

    response_text = generate_legal_chat_response(messages)
    return jsonify({"response": response_text})
