# backend/api/contract_context_routes.py

from flask import Blueprint, request, jsonify
from services.contract_context import get_contract_context
from utils.error_handler import handle_exceptions
from openai import OpenAIError
from config import OPENROUTER_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
contract_context_bp = Blueprint("contract_context", __name__)

@contract_context_bp.route("/generateContractContext", methods=["POST"])
@handle_exceptions
def generate_contract_context():
    print("ha entrado al endpoint")
    return jsonify({"prompt": "Título de prueba"}), 200
