from flask import Blueprint, request, jsonify
from config import OPENROUTER_API_KEY
from openai import OpenAI
from models.anonymizer import anonymize_text, revert_replacements

legalcheck_bp = Blueprint("legal_check", __name__)
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

@legalcheck_bp.route("/legalCheck", methods=["POST"])
def run_legal_check():
    try:
        data = request.get_json()
        original_content = data.get("content", "")
        contract_type = data.get("contract_type", "general")

        # 🔥 Anonimizar
        anonymized_content, replacements = anonymize_text(original_content)

        # Construir el prompt
        prompt = (
            f"Eres un abogado especializado en contratos del tipo '{contract_type}'.\n"
            f"Analiza de forma profesional y organizada el siguiente contrato.\n\n"
            f"CONTRATO:\n{anonymized_content}\n\n"
            f"Responde obligatoriamente siguiendo esta estructura:\n"
            f"1. **Sentido Jurídico:** Explica en pocas frases si el contrato tiene sentido jurídico general.\n"
            f"2. **Faltan Cláusulas Esenciales:** Enumera qué cláusulas importantes faltan, si corresponde.\n"
            f"3. **Incoherencias Legales o Riesgos:** Describe posibles incoherencias, riesgos o errores relevantes.\n"
            f"\n"
            f"Utiliza negritas para los títulos de cada sección.\n"
            f"No copies literalmente el contrato.\n"
            f"Escribe de manera clara, técnica y profesional como lo haría un abogado.\n"
        )


        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.2,
        )

        anonymized_analysis = response.choices[0].message.content.strip()

        # 🔥 Revertir el análisis para mostrar nombres reales si los menciona
        final_analysis = revert_replacements(anonymized_analysis, replacements)

        return jsonify({
            "analysis": final_analysis
        })

    except Exception as e:
        return jsonify({"error": "Error en verificación legal", "detail": str(e)}), 500
