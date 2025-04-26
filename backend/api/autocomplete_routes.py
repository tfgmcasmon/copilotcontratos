from flask import Blueprint, request, jsonify
from config import OPENROUTER_API_KEY
from openai import OpenAI
from utils.error_handler import handle_exceptions
import re

autocomplete_bp = Blueprint('autocomplete', __name__)
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

@autocomplete_bp.route('/trackChanges', methods=['POST'])
@handle_exceptions
def track_changes():
    data = request.get_json()
    text = data.get('changes', '').strip()
    contract_name = data.get('contract_name', 'Contrato General')

    if not text:
        return jsonify({"error": "No se recibió texto válido para cambios"}), 400

    # 🔥 Detectar sección actual
    text_upper = text.upper()
    if "CLÁUSULAS" in text_upper:
        section = "CLÁUSULAS"
    elif "EXPONEN" in text_upper:
        section = "EXPONEN"
    elif "REUNIDOS" in text_upper:
        section = "REUNIDOS"
    elif "FIRMAN" in text_upper or "FIRMA" in text_upper:
        section = "FIRMA FINAL"
    else:
        section = "INTRODUCCIÓN"

    # 🔥 Detectar última cláusula escrita
    clausulas = re.findall(r'(Primera|Segunda|Tercera|Cuarta|Quinta|Sexta|Séptima|Octava|Novena|Décima)', text, re.IGNORECASE)
    if clausulas:
        ult_clause = clausulas[-1]
        mapa_clausulas = {
            "Primera": "Segunda",
            "Segunda": "Tercera",
            "Tercera": "Cuarta",
            "Cuarta": "Quinta",
            "Quinta": "Sexta",
            "Sexta": "Séptima",
            "Séptima": "Octava",
            "Octava": "Novena",
            "Novena": "Décima",
            "Décima": "Undécima"
        }
        siguiente_clausula = mapa_clausulas.get(ult_clause.capitalize(), "Nueva Cláusula")
    else:
        siguiente_clausula = "Primera"

    # 🔥 Construir prompt adaptado según sección
    if section == "REUNIDOS":
        instructions = (
            "- NO repitas el título 'REUNIDOS'.\n"
            "- Presenta la segunda parte (nombre, dirección, DNI).\n"
            "- Usa placeholders como [NOMBRE], [DIRECCIÓN], [DNI].\n"
            "- Ejemplo: De otra parte, D./Dña. [NOMBRE], mayor de edad, con domicilio en [DIRECCIÓN], y N.I.F. número [DNI]."
        )
    elif section == "EXPONEN":
        instructions = (
            "- NO repitas el título 'EXPONEN'.\n"
            "- Continúa exponiendo motivos numerados (II., III., IV.).\n"
            "- Cada Exponen debe ser una frase jurídica breve y razonada.\n"
            "- No introducir cláusulas aquí."
        )
    elif section == "CLÁUSULAS":
        instructions = (
            "- Continúa redactando cláusulas numeradas.\n"
            f"- La siguiente cláusula es: {siguiente_clausula}.\n"
            "- Escribe el número ordinal y el título en negrita.\n"
            "- Después del título, redacta un párrafo breve y jurídico (mínimo 2-3 frases).\n"
            "- No repitas cláusulas anteriores.\n"
            "- No inventes nuevas secciones."
        )
    elif section == "FIRMA FINAL":
        instructions = (
            "- Redacta el cierre del contrato.\n"
            "- Indica lugar y fecha en formato: 'En [CIUDAD], a [FECHA]'.\n"
            "- Añade espacio para firma de las partes.\n"
            "- Ejemplo: [Firma del Arrendador]    [Firma del Arrendatario]"
        )
    else:
        instructions = (
            "- Continúa el contrato de manera coherente.\n"
            "- Introduce REUNIDOS o EXPONEN según corresponda.\n"
            "- No inventes cláusulas aún."
        )

    # 🔥 Montar el prompt final
    prompt = (
        f"Estás redactando un {contract_name}.\n\n"
        f"Sección actual: {section}.\n\n"
        f"Instrucciones específicas:\n{instructions}\n\n"
        f"Texto actual del contrato:\n{text}\n\n"
        "Continúa el contrato aquí:"
    )

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80,   # 🔥 Limitado para no sobreescribir
        temperature=0.2
    )

    completion = response.choices[0].message.content.strip()

    return jsonify({"autocomplete": completion}), 200
