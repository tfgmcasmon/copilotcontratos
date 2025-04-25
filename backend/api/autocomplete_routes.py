from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from openai import OpenAI, OpenAIError
from config import OPENROUTER_API_KEY
from services.contract_context import get_contract_context
from utils.cleaning import clean_and_cut_autocomplete

autocomplete_bp = Blueprint("autocomplete", __name__)
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

# Variable global para controlar el título inicial generado
last_generated_title = ""

@autocomplete_bp.route("/trackChanges", methods=["POST", "OPTIONS"])
@cross_origin()
def track_changes():
    global last_generated_title
    try:
        data = request.get_json()
        changes = data.get("changes", "").strip()
        contract_type = data.get("contract_type", "general")

        if not changes:
            return jsonify({"error": "No se recibieron cambios válidos"}), 400

        # Generar contexto según tipo de contrato
        context = get_contract_context(contract_type)

        # Enviar a modelo de lenguaje
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[{
                "role": "user",
                "content": f"{context}\nEl siguiente texto es parte de un contrato legal. Completa la cláusula de forma coherente, sin repetir palabras ya escritas ni empezar desde cero. Solo añade lo que falta:\n\n{changes}"
            }],
            max_tokens=50,
            temperature=0.2
        )

        completion = response.choices[0].message.content.strip()

        # Limpiar y recortar el autocompletado
        is_first_completion = changes == "" or last_generated_title in changes
        cleaned_completion = clean_and_cut_autocomplete(completion, changes, is_first_completion)

        if is_first_completion and cleaned_completion:
            last_generated_title = cleaned_completion.split("\n")[0]

        return jsonify({"autocomplete": cleaned_completion}), 200

    except OpenAIError as e:
        return jsonify({"error": "Error al generar el autocompletado", "error_detail": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Error interno del servidor", "error_detail": str(e)}), 500
