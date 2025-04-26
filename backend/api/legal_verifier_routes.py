from flask import Blueprint, request, jsonify
from openai import OpenAI
from config import OPENROUTER_API_KEY
from services.legal_analysis_service import preanalisis_estructural

legalcheck_bp = Blueprint("legal_check", __name__)
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

@legalcheck_bp.route("/legalCheck", methods=["POST"])
def run_legal_check():
    data = request.get_json()
    content = data.get("content", "")
    contract_type = data.get("contract_type", "general")

    # Aquí hacemos el análisis estructural previo
    analisis_prev = preanalisis_estructural(content)

    # Lo incluimos como parte del contexto al LLM
    resumen_prev = (
        f"Análisis estructural:\n"
        f"- Artículos legales detectados: {', '.join(analisis_prev['articulos_legales']) or 'ninguno'}\n"
        f"- Secciones clave encontradas: {', '.join(analisis_prev['secciones_clave']) or 'ninguna'}\n"
        f"- Campos vacíos: {', '.join(analisis_prev['placeholders_detectados']) or 'ninguno'}\n\n"
    )

    prompt = (
        f"Eres un abogado especializado en contratos de tipo '{contract_type}'.\n"
        f"Analiza el siguiente contrato y ten en cuenta el análisis previo del sistema.\n"
        f"{resumen_prev}"
        f"CONTRATO:\n{content}\n\n"
        f"Indica:\n"
        f"- Si tiene sentido jurídico\n"
        f"- Si los artículos están bien usados\n"
        f"- Si faltan cláusulas esenciales o hay incoherencias"
    )

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.2,
        )
        result = response.choices[0].message.content.strip()
        return jsonify({
            "analysis": result,
            "estructura": analisis_prev
        })

    except Exception as e:
        return jsonify({"error": "Error en verificación legal", "detail": str(e)}), 500
