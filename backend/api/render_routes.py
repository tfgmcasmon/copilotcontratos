# backend/api/render_routes.py

from flask import Blueprint, request, jsonify
from config import OPENROUTER_API_KEY
from openai import OpenAI
from utils.error_handler import handle_exceptions

render_bp = Blueprint("render", __name__)
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

@render_bp.route("/renderContract", methods=["POST"])
@handle_exceptions
def render_contract():
    data = request.get_json()
    contract_text = data.get("content", "").strip()

    if not contract_text:
        return jsonify({"error": "El contenido está vacío"}), 400

    prompt = (
        "Recibes un contrato en texto plano. "
        "Devuélvelo formateado en HTML limpio, usando <strong> para los títulos de cláusulas importantes "
        "y <p> para cada párrafo. No inventes contenido adicional. No pongas CSS.\n\n"
        f"Contrato:\n{contract_text}"
    )

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.2
    )

    rendered_html = response.choices[0].message.content.strip()
    return jsonify({"rendered_html": rendered_html}), 200
