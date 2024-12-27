import json
import spacy
from flask_cors import CORS
from openai import OpenAI, OpenAIError
from flask import Flask, request, jsonify
import re

# Configuración de la API Key
with open('secrets.json', 'r') as file:
    SECRETS = json.load(file)

app = Flask(__name__)
CORS(app)

# Configuración del cliente OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=SECRETS["openai_api_key"],
)

# Carga el modelo de spaCy en español
nlp = spacy.load("es_core_news_md")


def anonymize_text(text):
    """
    Anonimiza datos sensibles como nombres, DNI y teléfonos en el texto.
    """
    replacements = {}  # Mapeo de marcadores a datos sensibles

    # Detecta entidades en el texto usando spaCy
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["PER", "LOC", "ORG"]:  # Personas, lugares, organizaciones
            key = f"<{ent.label_}{len(replacements)}>"
            replacements[key] = ent.text
            text = text.replace(ent.text, key)

    # Reemplazo adicional para DNI
    text = replace_pattern(text, r'\b\d{8}[A-Z]\b', "DNI", replacements)

    # Reemplazo adicional para teléfonos
    text = replace_pattern(text, r'\b(6|7)\d{8}\b', "TELEFONO", replacements)

    return text, replacements


def replace_pattern(text, pattern, label, replacements):
    """
    Reemplaza un patrón específico (como DNI o teléfono) en el texto.
    """
    matches = re.findall(pattern, text)
    for match in matches:
        key = f"<{label}{len(replacements)}>"
        replacements[key] = match
        text = text.replace(match, key)
    return text


@app.route('/trackChanges', methods=['POST'])
def track_changes():
    """
    Procesa cambios enviados desde el frontend y responde con texto autocompletado.
    """
    try:
        data = request.json
        changes = data.get('changes', '')

        if not changes.strip():
            return jsonify({"error": "No se recibieron cambios válidos"}), 400

        # Anonimiza el texto recibido
        anonymized_text, replacements = anonymize_text(changes)

        # Enviar el texto anonimizado al modelo de IA para autocompletado
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[
                {
                    "role": "user",
                    "content": f"Continúa el texto de manera coherente: {anonymized_text}"
                }
            ],
            max_tokens=100,
            temperature=0.3
        )

        completion = response.choices[0].message.content.strip()
        print(f"Autocompletado generado: {completion}")

        # Devuelve el texto autocompletado y los reemplazos al frontend
        return jsonify({
            "autocomplete": completion,
            "replacements": replacements
        }), 200

    except OpenAIError as e:
        print(f"Error al conectar con OpenAI: {e}")
        return jsonify({"error": "Error al generar el autocompletado", "error_detail": str(e)}), 500

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": "Error interno del servidor", "error_detail": str(e)}), 500


@app.route('/formatToLatex', methods=['POST'])
def format_to_latex():
    """
    Convierte el texto recibido en formato LaTeX con encabezados básicos.
    """
    try:
        data = request.json
        text = data.get('text', '')

        if not text.strip():
            return jsonify({"error": "No se recibió texto válido"}), 400

        # Enviar el texto al modelo de IA para formatear en LaTeX
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[
                {
                    "role": "user",
                    "content": f"Convierte el siguiente texto en un documento LaTeX bien formateado con encabezados básicos: {text}"
                }
            ],
            max_tokens=500,
            temperature=0.3
        )

        raw_response = response.choices[0].message.content.strip()

        # Extraer solo el bloque LaTeX
        start = raw_response.find("\\documentclass")
        end = raw_response.rfind("\\end{document}") + len("\\end{document}")
        if start != -1 and end != -1:
            latex_code = raw_response[start:end]
        else:
            latex_code = raw_response  # Devuelve el texto completo si no encuentra delimitadores

        # Asegurar que se incluye un título básico y encabezados
        if "\\documentclass" not in latex_code:
            latex_code = (
                "\\documentclass{article}\n"
                "\\usepackage[utf8]{inputenc}\n"
                "\\usepackage[spanish]{babel}\n"
                "\\begin{document}\n"
                f"{latex_code}\n"
                "\\end{document}"
            )

        return jsonify({
            "latex": latex_code
        }), 200

    except OpenAIError as e:
        print(f"Error al conectar con OpenAI: {e}")
        return jsonify({"error": "Error al generar el formato LaTeX", "error_detail": str(e)}), 500

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": "Error interno del servidor", "error_detail": str(e)}), 500

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """
    Verifica que el servidor y los servicios estén activos.
    """
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{"role": "user", "content": "Hola, ¿puedes confirmar que la API está funcionando?"}],
        )
        api_response = response.choices[0].message.content

        return jsonify({"status": "ok", "api_response": api_response}), 200

    except OpenAIError as e:
        print(f"Error de OpenAI: {e}")
        return jsonify({"status": "error", "message": "Error al conectar con la API", "error_detail": str(e)}), 500

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor", "error_detail": str(e)}), 500


@app.route('/testpost', methods=['POST'])
def test_post():
    """
    Ruta de prueba para validar envíos POST.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se recibió un cuerpo JSON válido"}), 400

        return jsonify({"status": "ok", "message": "Datos recibidos correctamente", "received_data": data}), 200

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor", "error_detail": str(e)}), 500


if __name__ == "__main__":
    print("Servidor Flask corriendo en http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=True)
