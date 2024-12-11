import json
import openai
from flask_cors import CORS
from openai import OpenAI, OpenAIError
from flask import Flask, request, jsonify, make_response

# Configuración de la API Key

# Read JSON from a file
with open('secrets.json', 'r') as file:
    SECRETS = json.load(file)

app = Flask(__name__)
CORS(app)
#CORS(app, resources={r"/*": {"origins": "*"}})

openai_api_key = SECRETS["openai_api_key"]

# OpenAI client initialize
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=SECRETS["openai_api_key"],
    )

def filter_redundant_phrases(phrases):
    """
    Elimina frases duplicadas o redundantes en una lista.
    """
    seen = set()
    filtered = []
    for phrase in phrases:
        if phrase.lower() not in seen:  # Ignorar duplicados (sin sensibilidad a mayúsculas)
            filtered.append(phrase)
            seen.add(phrase.lower())
    return filtered

@app.route('/trackChanges', methods=['POST'])
def track_changes():
    try:
        data = request.json
        changes = data.get('changes', '')

        if not changes.strip():
            return jsonify({"error": "No se recibieron cambios válidos"}), 400

        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{"role": "user", "content": f"Continúa el texto de forma coherente y lógica: {changes}"}],
            max_tokens=100,
            temperature=0.1
        )

        completion = response.choices[0].message.content.strip()
        print(f"Respuesta de OpenAI: {completion}")  # Log para verificar
        return jsonify({"input": changes, "autocomplete": completion}), 200

    except OpenAIError as e:
        print(f"Error al conectar con OpenAI: {e}")  # Log más detallado
        return jsonify({"error": "Error al generar la sugerencia con IA", "error_detail": str(e)}), 500

    except Exception as e:
        print(f"Error inesperado: {e}")  # Captura errores generales
        return jsonify({"error": "Error interno del servidor", "error_detail": str(e)}), 500

@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    """
    Ruta para comprobar que el backend y la conexión con la API están funcionando.
    """
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{"role": "user", "content": "Hola, ¿puedes confirmar que la API está funcionando?"}],
        )
        api_response = response.choices[0].message.content

        return jsonify({
            "status": "ok",
            "api_response": api_response
        }), 200

    except OpenAIError as e:
        print(f"Error de OpenAI: {e}")
        return jsonify({
            "status": "error",
            "message": "Error al conectar con la API",
            "error_detail": str(e)
        }), 500

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor",
            "error_detail": str(e)
        }), 500

@app.route("/testpost", methods=["POST"])
def test_post():
    """
    Ruta POST para probar la recepción de datos y devolver una respuesta sencilla.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se recibió un cuerpo JSON válido"}), 400

        return jsonify({
            "status": "ok",
            "message": "Datos recibidos correctamente",
            "received_data": data
        }), 200

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor",
            "error_detail": str(e)
        }), 500

@app.route("/suggestions", methods=["POST"])
def get_suggestions():
    """
    Genera sugerencias con OpenAI basadas en el texto de entrada.
    """
    print("Solicitud POST recibida en /suggestions")

    try:
        data = request.json
        print(f"Datos recibidos: {data}")

        input_text = data.get("input", "")

        if not input_text.strip():
            return jsonify({"error": "El campo 'input' está vacío", "suggestions": []}), 400

        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{
                "role": "user",
                "content": f"Proporciona sugerencias claras y únicas para: {input_text}",
            }],
            max_tokens=150,
            temperature=0.1
        )

        # Extraer texto y filtrar redundancias
        raw_suggestions = response.choices[0].message.content.strip().split("\n")
        suggestions = filter_redundant_phrases(raw_suggestions)

        print(f"Sugerencias generadas: {suggestions}")
        return jsonify({"suggestions": suggestions}), 200

    except openai.OpenAIError as e:
        print(f"Error de OpenAI: {e}")
        return jsonify({"error": "Error al generar sugerencias con OpenAI", "suggestions": []}), 500

    except Exception as e:
        print(f"Error inesperado en el servidor: {e}")
        return jsonify({"error": "Error interno del servidor", "suggestions": []}), 500

if __name__ == "__main__":
    print("Servidor Flask corriendo en http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=True)
