import json
import spacy
from flask_cors import CORS
from openai import OpenAI, OpenAIError
from flask import Flask, request, jsonify
import re
from collections import deque
from difflib import SequenceMatcher
from collections import defaultdict
from sentence_transformers import SentenceTransformer
import faiss
import os
from buscar_fragmentos import get_fragmentos_legales

# Cargar modelo y FAISS solo una vez
embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
faiss_index = faiss.read_index("data/faiss_index.bin")


# Carga de los metadatos de los fragmentos
with open("data/fragmentos_metadata.json", "r", encoding="utf-8") as f:
    fragmentos_metadata = json.load(f)

def format_response(raw_text):
    raw_text = raw_text.replace("Cita:", "<br><strong>Cita:</strong><ul>")
    raw_text = re.sub(r"- (c_digo_[a-z]+), artículo (\d+):", r"<li><strong>\2:</strong> ", raw_text)
    raw_text = raw_text.replace("...", "</li></ul>")
    raw_text = raw_text.replace("c_digo_civil", "Código Civil").replace("c_digo_penal", "Código Penal")
    return raw_text


def buscar_fragmentos_contexto(pregunta, top_k=5):
    vector = embedding_model.encode([pregunta])
    _, indices = faiss_index.search(vector, top_k)

    fragmentos = []
    for i in indices[0]:
        item = fragmentos_metadata[i]
        fragmentos.append(f"- **{item['ley']}**, artículo {item['id']}:\n{item['texto']}")
    return "\n\n".join(fragmentos)


# Guardamos el título inicial para evitar repetirlo en el primer tab
last_generated_title = ""

#Memoria del contexto
history=deque(maxlen=20)

# Configuración de la API Key
with open(os.path.join(os.path.dirname(__file__), '..', 'secrets.json'), 'r', encoding='utf-8') as file:
    SECRETS = json.load(file)

app = Flask(__name__)
CORS(app)
nlp = spacy.load("es_core_news_md")

# Configuración del cliente OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=SECRETS["openai_api_key"],
)


def nombres_similares(nombre1, nombre2, umbral=0.8):
    return SequenceMatcher(None, nombre1.lower(), nombre2.lower()).ratio() >= umbral

def extraer_y_validar_dnis(texto):
    """
    Extrae todos los DNIs del texto y devuelve cuáles son inválidos.
    """
    posibles_dnis = re.findall(r'\b\d{8}[A-Z]\b', texto.upper())
    dnis_invalidos = []

    for dni in posibles_dnis:
        if not validar_dni_espanol(dni):
            dnis_invalidos.append(dni)

    return dnis_invalidos


def validar_dni_espanol(dni):
    """
    Verifica si un DNI español es válido (formato y letra).
    """
    dni = dni.strip().upper()
    if not re.match(r'^\d{8}[A-Z]$', dni):
        return False

    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    numero = int(dni[:-1])
    letra_correcta = letras[numero % 23]

    return dni[-1] == letra_correcta

def normalizar_nombre(nombre):
    """
    Convierte el nombre a minúsculas y elimina caracteres no alfabéticos (excepto espacios).
    """
    nombre = nombre.lower().strip()
    return re.sub(r'[^a-záéíóúñ\s]', '', nombre)
    
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
    
@app.route('/verifyContractData', methods=['POST'])
def verify_contract_data():
    try:
        data = request.json
        contract_text = data.get("contract_text", "").strip()

        if not contract_text:
            return jsonify({"error": "No se recibió texto del contrato"}), 400

        doc = nlp(contract_text)
        issues = []

        person_data = {}  # persona -> datos
        global_dnis = {}
        global_telefonos = defaultdict(set)

        for sent in doc.sents:
            sentence = sent.text
            sent_doc = nlp(sentence)

            # Buscar nombres de persona
            nombres = [ent.text.strip() for ent in sent_doc.ents if ent.label_ == "PER"]
            if not nombres:
                continue

            # Asignar todos los datos de esta frase a estos nombres
            posibles_dnis = re.findall(r'\b\d{7,8}[A-Za-z]\b', sentence)
            telefonos = re.findall(r'\b6\d{8}\b|\b7\d{8}\b', sentence)
            direccion = re.search(r'\b(calle|av(enida)?|plaza|camino|paseo)\s+[^\.,\n]+', sentence, re.IGNORECASE)

            for nombre in nombres:
                nombre_key = nombre.lower()
                if nombre_key not in person_data:
                    person_data[nombre_key] = {
                        "nombre_original": nombre,
                        "dnis": set(),
                        "telefonos": set(),
                        "direcciones": set()
                    }

                for dni in posibles_dnis:
                    person_data[nombre_key]["dnis"].add(dni.upper())

                for tel in telefonos:
                    person_data[nombre_key]["telefonos"].add(tel)
                    global_telefonos[tel].add(nombre_key)

                if direccion:
                    person_data[nombre_key]["direcciones"].add(direccion.group().strip())

        # Detectar errores
        for persona, datos in person_data.items():
            nombre_mostrado = datos["nombre_original"]

            # Formato de nombre sospechoso
            if not re.match(r"^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+$", nombre_mostrado):
                issues.append(f"⚠️ Formato de nombre inusual: '{nombre_mostrado}'")

            # Múltiples DNIs para una persona
            if len(datos["dnis"]) > 1:
                issues.append(f"❌ '{nombre_mostrado}' tiene múltiples DNIs: {', '.join(datos['dnis'])}")

            for dni in datos["dnis"]:
                if not validar_dni_espanol(dni):
                    issues.append(f"⚠️ DNI potencialmente incorrecto para '{nombre_mostrado}': {dni}")

                if dni in global_dnis and global_dnis[dni] != persona:
                    otra = person_data[global_dnis[dni]]["nombre_original"]
                    issues.append(f"❌ DNI '{dni}' está asociado a múltiples personas: '{nombre_mostrado}' y '{otra}'")
                else:
                    global_dnis[dni] = persona

            # Guardar teléfonos ya advertidos para evitar duplicados
            telefonos_reportados = set()

            telefonos_reportados = set()

            for tel in datos["telefonos"]:
                if len(global_telefonos[tel]) > 1 and tel not in telefonos_reportados:
                    personas_con_tel = [person_data[p]["nombre_original"] for p in global_telefonos[tel]]
                    mensaje = f"❌ El teléfono '{tel}' está siendo usado por múltiples personas: {', '.join(personas_con_tel)}."
                    if mensaje not in issues:
                        issues.append(mensaje)
                    telefonos_reportados.add(tel)



        return jsonify({"issues": issues}), 200

    except Exception as e:
        print(f"Error en verificación: {e}")
        return jsonify({"error": "Error interno al verificar los datos", "detail": str(e)}), 500

@app.route('/legalChat', methods=['POST'])
def legal_chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        if not messages:
            return jsonify({"error": "No se recibió historial de mensajes."}), 400

        pregunta_usuario = messages[-1]["content"]

        # Recuperar fragmentos legales completos
        fragmentos = get_fragmentos_legales(pregunta_usuario)
    

        # Construir contexto legal con formato
        contexto = "\n\n".join([
            f"📘 **Ley:** {f['ley_id'].replace('_', ' ').title()}\n📝 **Artículo {f['articulo']}**\n{f['texto']}"
            for f in fragmentos
        ])

        # Prompt con contexto legal
        prompt = (
            f"Teniendo en cuenta los siguientes artículos relevantes:\n\n{contexto}\n\n"
            f"Responde a la pregunta legal en español claro, sin inventar información. "
            f"Usa formato visual (negritas, listas) si es útil. La pregunta es:\n\n"
            f"{pregunta_usuario}"
        )

        # Llamada a Mistral vía OpenRouter
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=700
        )

        answer = response.choices[0].message.content.strip()

        # Generar las citas legales completas al final
        referencias = []
        for frag in fragmentos:
            ley_legible = frag["ley_id"].replace("_", " ").replace("c digo", "Código").title()
            articulo = frag["articulo"]
            texto = frag["texto"].strip()

            # Cortar si es muy largo
            if len(texto.split()) > 150:
                texto = " ".join(texto.split()[:150]) + "..."

            referencia = f"**{ley_legible}, artículo {articulo}.** {texto}"
            referencias.append(referencia)

        # Añadir al final de la respuesta
        if referencias:
            answer += "\n\n---\n\n**📚 Leyes citadas:**\n\n" + "\n\n".join(referencias)

        return jsonify({"response": answer}), 200


    except Exception as e:
        print(f"❌ Error en /legalChat: {e}")
        return jsonify({"error": "Error interno al procesar la consulta legal."}), 500
        
if __name__ == "__main__":
    print("Servidor Flask corriendo en http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=True)
