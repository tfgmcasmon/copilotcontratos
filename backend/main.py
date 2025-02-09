import json
import spacy
from flask_cors import CORS
from openai import OpenAI, OpenAIError
from flask import Flask, request, jsonify
import re
from collections import deque

# Guardamos el título inicial para evitar repetirlo en el primer tab
last_generated_title = ""

#Memoria del contexto
history=deque(maxlen=20)

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


def clean_and_cut_autocomplete(text, existing_text, is_first_completion):
    """
    Limpia el autocompletado eliminando placeholders, corta el texto donde el usuario debe introducir datos,
    y evita repetir el título en la primera sugerencia.
    """
    global last_generated_title  # Usamos la variable global

    text = text.strip()

    # 🚨 1. Evitar la repetición del título en la primera sugerencia
    if is_first_completion and last_generated_title:
        normalized_title = re.sub(r'[^a-zA-Z0-9]', '', last_generated_title.lower())  # Normalizar sin caracteres especiales
        normalized_text = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
        if normalized_text.startswith(normalized_title):
            text = text[len(last_generated_title):].strip()

    # 🚨 2. Definir patrones de placeholders comunes
    placeholders = [
        r"\[.*?\]", r"\(.*?\)", r"\{.*?\}", r"XXXX+", r"DNI:\s*X{6,10}",
        r"DNI/NIE:\s*_+", r"Dirección:\s*_+", r"Fecha:\s*\d{0,2}/\d{0,2}/\d{0,4}",
        r"_{2,}", r"\.\.\.", r'" "', r"\s*_\s*", 
        r"\bNOMBRE COMPLETO DEL COMPRADOR\b", r"\bDNI/NIE DEL COMPRADOR\b",
        r"\bDIRECCIÓN DEL COMPRADOR\b", r"\bFECHA DEL CONTRATO\b", r"\b[A-Z\s]{3,}\b"
    ]

    # 🚨 3. Cortar en el primer placeholder encontrado
    for pattern in placeholders:
        match = re.search(pattern, text)
        if match:
            text = text[:match.start()].strip()
            break

    # 🚨 4. Evitar que el autocompletado agregue saltos de línea
    if "\n" in text:
        text = text.replace("\n", " ")

    # 🚨 5. Si el texto ya existe en el historial, no lo mostramos
    normalized_existing = re.sub(r'\s+', ' ', existing_text.lower().strip())
    normalized_text = re.sub(r'\s+', ' ', text.lower().strip())

    if normalized_text in normalized_existing:
        return ""

    return text


def anonymize_text(text):
    """
    Anonimiza datos sensibles como nombres, DNI, teléfonos y direcciones en el texto.
    """
    replacements = {}
    
    # Anonimizar nombres, organizaciones y ubicaciones con spaCy
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["PER", "LOC", "ORG"]:
            key = f"<{ent.label_}{len(replacements)}>"
            replacements[key] = ent.text
            text = text.replace(ent.text, key)

    # Anonimizar DNI (Formato español: 8 números + 1 letra)
    text = replace_pattern(text, r'\b\d{8}[A-Z]\b', "DNI", replacements)

    #  anonimizar cualquier número de teléfono (9+ dígitos seguidos)
    text = replace_pattern(text, r'\b\d{9,}\b', "TELEFONO", replacements)

    # Anonimizar direcciones basadas en palabras clave comunes
    residencia_patterns = [
        r"\b(vive en [\w\s,]+)",
        r"\b(reside en [\w\s,]+)",
        r"\b(con domicilio en [\w\s,]+)",
        r"\b(con residencia en [\w\s,]+)",
        r"\b(ubicado en [\w\s,]+)",
        r"\b(situado en [\w\s,]+)",
        r"\b(domiciliado en [\w\s,]+)",
        r"\b(se encuentra en [\w\s,]+)"
    ]

    for pattern in residencia_patterns:
        text = replace_pattern(text, pattern, "DIRECCION", replacements)

    return text, replacements



def replace_pattern(text, pattern, label, replacements):
    """
    Reemplaza patrones específicos (DNI, teléfono) en el texto.
    """
    matches = list(re.finditer(pattern, text))  # Encuentra todas las coincidencias
    
    for match in matches:
        value = match.group()  # Extrae el valor encontrado
        key = f"<{label}{len(replacements)}>"
        
        # Evita reemplazos duplicados
        if value not in replacements.values():
            replacements[key] = value
            text = re.sub(rf'\b{re.escape(value)}\b', key, text, count=1)

    return text


def get_contract_context(contract_type):
    """
    Genera un contexto detallado en función del tipo de contrato seleccionado.
    Proporciona información clave para que la IA pueda generar contenido más preciso.
    """

    if contract_type == "arras":
        return (
            "Estás redactando un **contrato de arras**, que es un acuerdo previo a la compraventa de un inmueble. "
            "En este contrato, el comprador entrega una cantidad de dinero al vendedor como señal para reservar el inmueble. "
            "Se deben incluir los siguientes elementos clave:\n"
            "- **Identificación de las partes:** Nombre, apellidos, DNI/NIE y domicilio del comprador y vendedor.\n"
            "- **Descripción del inmueble:** Dirección exacta, referencia catastral y características del bien.\n"
            "- **Importe de las arras:** Cantidad entregada y su impacto en el precio final.\n"
            "- **Condiciones de devolución o pérdida de las arras:** Consecuencias de incumplimiento por ambas partes.\n"
            "- **Plazo de ejecución de la compraventa:** Fecha límite para la firma del contrato definitivo.\n"
            "El lenguaje debe ser claro, evitando ambigüedades para garantizar seguridad jurídica."
        )

    elif contract_type == "compraventa":
        return (
            "Estás redactando un **contrato de compraventa**, que formaliza la transferencia de propiedad de un bien a cambio de un precio pactado. "
            "Este contrato debe contener los siguientes elementos esenciales:\n"
            "- **Identificación del comprador y del vendedor:** Nombre completo, DNI/NIE, domicilio y contacto.\n"
            "- **Descripción del bien objeto de la compraventa:** Detalles precisos del inmueble o bien en cuestión.\n"
            "- **Precio y forma de pago:** Importe acordado, método de pago, plazos y posibles cláusulas de financiación.\n"
            "- **Entrega del bien:** Fecha y condiciones bajo las cuales se hará la entrega de la propiedad.\n"
            "- **Garantías y cargas del bien:** Estado legal del bien, hipotecas, embargos o limitaciones.\n"
            "- **Cláusula de resolución:** Situaciones en las que el contrato puede anularse o modificarse.\n"
            "El tono del documento debe ser formal y reflejar fielmente los acuerdos entre las partes."
        )

    elif contract_type == "arrendamiento":
        return (
            "Estás redactando un **contrato de arrendamiento**, un acuerdo en el que el arrendador cede el uso de un inmueble al arrendatario "
            "a cambio de una renta periódica. Para que sea válido, debe incluir los siguientes elementos:\n"
            "- **Identificación del arrendador y arrendatario:** Nombres completos, DNI/NIE y domicilios.\n"
            "- **Descripción del inmueble arrendado:** Ubicación, características y estado de conservación.\n"
            "- **Duración del contrato:** Fecha de inicio y finalización, con posibilidad de renovación o prórroga.\n"
            "- **Renta y forma de pago:** Monto mensual, fechas de pago y métodos aceptados.\n"
            "- **Gastos y mantenimiento:** Quién asume los costos de servicios, reparaciones y comunidad.\n"
            "- **Condiciones de rescisión:** Situaciones en las que cualquiera de las partes puede dar por finalizado el contrato.\n"
            "El documento debe garantizar la protección tanto del propietario como del inquilino, asegurando claridad y transparencia en sus términos."
        )

    else:
        return (
            "Estás redactando un **contrato legal**, en el que es fundamental incluir información estructurada sobre:\n"
            "- **Las partes involucradas:** Identificación completa de los firmantes.\n"
            "- **Objeto del contrato:** Qué se está acordando y bajo qué condiciones.\n"
            "- **Duración y vigencia:** Fecha de inicio y finalización, si aplica.\n"
            "- **Obligaciones y derechos de cada parte:** Responsabilidades y derechos establecidos.\n"
            "- **Condiciones de pago o contraprestación:** En caso de que haya intercambio de bienes o dinero.\n"
            "- **Cláusulas adicionales:** Posibles penalizaciones, resolución de disputas, confidencialidad, etc.\n"
            "El lenguaje debe ser claro, directo y jurídicamente sólido, asegurando que no haya ambigüedades."
        )


@app.route('/generateContractContext', methods=['POST'])
def generate_contract_context():
    """
    Genera un contexto inicial basado en el tipo de contrato seleccionado.
    Se asegura de que el modelo devuelva solo el título correctamente formateado.
    """
    try:
        data = request.json
        contract_type = data.get('contract_type', 'general')
        context = get_contract_context(contract_type)

        # Definir la instrucción con mayor precisión
        prompt = (
            f"{context}\n"
            "Genera exclusivamente un título corto y descriptivo para este contrato en español. "
            "NO incluyas una introducción ni ninguna otra información adicional. "
            "Responde solo con el título en una sola línea."
        )

        # Llamada a OpenAI
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,  # Limitamos la longitud del título
            temperature=0.2
        )

        initial_prompt = response.choices[0].message.content.strip()

        # Verificar que la respuesta no tenga varias líneas
        if "\n" in initial_prompt:
            print("Error en la respuesta de la IA: La respuesta del modelo no contiene el formato esperado.")
            return jsonify({"error": "La IA devolvió una respuesta inesperada"}), 500

        print(f"Contexto inicial generado: {initial_prompt}")

        return jsonify({"prompt": initial_prompt}), 200

    except OpenAIError as e:
        print(f"Error al conectar con OpenAI: {e}")
        return jsonify({"error": "Error al generar el contexto del contrato", "error_detail": str(e)}), 500

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": "Error interno del servidor", "error_detail": str(e)}), 500


@app.route('/trackChanges', methods=['POST'])
def track_changes():
    """
    Procesa cambios desde el frontend y genera autocompletado sin placeholders incorrectos ni repeticiones.
    """
    global last_generated_title

    try:
        data = request.json
        changes = data.get('changes', '').strip()
        contract_type = data.get('contract_type', 'general')

        if not changes:
            return jsonify({"error": "No se recibieron cambios válidos"}), 400

        context = get_contract_context(contract_type)

        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{
                "role": "user",
                "content": f"{context} Continúa el siguiente texto, evitando placeholders y repeticiones: {changes}"
            }],
            max_tokens=50,
            temperature=0.2
        )

        completion = response.choices[0].message.content.strip()

        # 🚨 Si es la primera sugerencia, evitar repetir el título
        is_first_completion = changes == "" or last_generated_title in changes
        cleaned_completion = clean_and_cut_autocomplete(completion, changes, is_first_completion)

        # 🚨 Guardar título generado para futuras comparaciones
        if is_first_completion and cleaned_completion:
            last_generated_title = cleaned_completion.split("\n")[0]

        print(f"Autocompletado generado: {cleaned_completion}")

        return jsonify({"autocomplete": cleaned_completion}), 200

    except OpenAIError as e:
        print(f"Error al conectar con OpenAI: {e}")
        return jsonify({"error": "Error al generar el autocompletado", "error_detail": str(e)}), 500

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": "Error interno del servidor", "error_detail": str(e)}), 500


if __name__ == "__main__":
    print("Servidor Flask corriendo en http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=True)
