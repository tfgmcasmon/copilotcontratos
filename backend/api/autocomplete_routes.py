from flask import Blueprint, request, jsonify
from config import OPENROUTER_API_KEY
from openai import OpenAI
from utils.error_handler import handle_exceptions
from models.anonymizer import anonymize_text, revert_replacements
import re

autocomplete_bp = Blueprint('autocomplete', __name__)
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

@autocomplete_bp.route('/trackChanges', methods=['POST'])
@handle_exceptions
def track_changes():
    data = request.get_json()
    original_text = data.get('changes', '').strip()
    contract_name = data.get('contract_name', 'Contrato General')

    if not original_text:
        return jsonify({"error": "No se recibió texto válido para cambios"}), 400

    #  Anonimizar el texto antes de enviarlo a la IA
    anonymized_text, replacements = anonymize_text(original_text)

    # Detectar la sección basada en texto original (mejor para detección humana)
    section_match = re.findall(r'^[A-ZÁÉÍÓÚÑ ]{4,}$', original_text, re.MULTILINE)
    if section_match:
        section = section_match[-1].strip()
    else:
        section = "INTRODUCCIÓN"

    # Clasificar la sección
    section_upper = section.upper()
    logical_section = (
        "REUNIDOS" if "REUNIDOS" in section_upper else
        "EXPONEN" if "EXPONEN" in section_upper else
        "CLÁUSULAS" if "CLÁUSULAS" in section_upper else
        "FIRMA FINAL" if "FIRMAN" in section_upper or "FIRMA" in section_upper else
        "ANEXOS" if "ANEXO" in section_upper else
        "CONDICIONES PARTICULARES" if "CONDICIONES PARTICULARES" in section_upper else
        "SECCIÓN PERSONALIZADA"
    )

    # Detectar última cláusula para numeración
    clausulas = re.findall(r'(Primera|Segunda|Tercera|Cuarta|Quinta|Sexta|Séptima|Octava|Novena|Décima)', original_text, re.IGNORECASE)
    if clausulas:
        ult_clause = clausulas[-1].capitalize()
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
        siguiente_clausula = mapa_clausulas.get(ult_clause, "Nueva cláusula")
    else:
        siguiente_clausula = "Primera"

    # Instrucciones específicas por sección (como definimos antes)
    instructions = {
        "REUNIDOS": (
            "- Presenta los datos de las partes (nombre, dirección, NIF) usando placeholders [NOMBRE], [DIRECCIÓN], [DNI].\n"
            "- No repitas 'REUNIDOS'. Sé formal y breve."
        ),
        "EXPONEN": (
            "- Expón motivos jurídicos sólidos, en numeración romana (II., III., IV.).\n"
            "- Cada motivo debe explicar razones legales (capacidad, propiedad, voluntad, etc.).\n"
            "- No repitas 'EXPONEN'. Sé claro y formal."
        ),
        "CLÁUSULAS": (
            f"- La siguiente cláusula debe comenzar con: {siguiente_clausula}.\n"
            "- Escribe el número ordinal seguido de un título breve.\n"
            "- Después, OBLIGATORIAMENTE redacta un párrafo jurídico explicativo de mínimo 3 frases.\n"
            "- NO se acepta solo título. Si escribes solo el título, se considerará incompleto.\n"
            "- Cada cláusula debe abordar un tema distinto (Duración, Precio, Entrega, Garantías, Resolución de Conflictos, etc.).\n"
            "- Usa lenguaje jurídico formal, claro y técnico."
        ),
        "FIRMA FINAL": (
            "- Redacta el cierre del contrato: lugar, fecha y espacio para firmas.\n"
            "- No introduzcas nuevas cláusulas aquí."
        ),
        "ANEXOS": (
            "- Redacta una LISTA ENUMERADA de entregables, productos o documentos concretos.\n"
            "- No escribas párrafos largos.\n"
            "- Ejemplo:\n"
            "  - Producto A\n"
            "  - Producto B\n"
            "  - Documento C\n"
            "- Sé específico, breve y técnico."
        ),
        "CONDICIONES PARTICULARES": (
            "- Redacta condiciones especiales adaptadas a este contrato.\n"
            "- Sé preciso, jurídico y técnico."
        ),
        "SECCIÓN PERSONALIZADA": (
            "- Analiza el contenido anterior.\n"
            "- Continúa de forma coherente, formal y adaptada al tipo de contrato.\n"
            "- Usa lenguaje jurídico claro y técnico."
        ),
    }


    # Montar prompt adaptado
    prompt = (
        f"Estás redactando un contrato titulado '{contract_name}'.\n\n"
        f"Sección actual detectada: {section}.\n\n"
        "Instrucciones específicas:\n"
        f"{instructions.get(logical_section, instructions['SECCIÓN PERSONALIZADA'])}\n\n"
        "Normas adicionales:\n"
        "- No inventes datos personales.\n"
        "- Usa placeholders como [NOMBRE], [DIRECCIÓN], [DNI], [FECHA], [IMPORTE].\n"
        "- Escribe en español formal, jurídico y técnico.\n"
        "- Si no hay nada relevante que continuar, responde 'No sugerir nada'.\n\n"
        f"Texto actual del contrato:\n{anonymized_text}\n\n"
        "Continúa el contrato aquí:"
    )

    #  Llamada a la IA
    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.2
    )

    anonymized_completion = response.choices[0].message.content.strip()


    #  Revertir reemplazos para el usuario
    final_completion = revert_replacements(anonymized_completion, replacements)

    return jsonify({"autocomplete": final_completion}), 200
