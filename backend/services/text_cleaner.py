import re

# Variable auxiliar para controlar si el primer título generado se repite
last_generated_title = ""

def clean_and_cut_autocomplete(text, existing_text, is_first_completion):
    global last_generated_title

    text = text.strip()

    # Evitar repetir el título en la primera sugerencia
    if is_first_completion and last_generated_title:
        normalized_title = re.sub(r'[^a-zA-Z0-9]', '', last_generated_title.lower())
        normalized_text = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
        if normalized_text.startswith(normalized_title):
            text = text[len(last_generated_title):].strip()

    # Patrones de placeholders o contenido incompleto a eliminar
    placeholders = [
        r"\[.*?\]", r"\(.*?\)", r"\{.*?\}", r"XXXX+", r"DNI:\s*X{6,10}",
        r"DNI/NIE:\s*_+", r"Dirección:\s*_+", r"Fecha:\s*\d{0,2}/\d{0,2}/\d{0,4}",
        r"_{2,}", r"\.\.\.", r'" "', r"\s*_\s*",
        r"\bNOMBRE COMPLETO DEL COMPRADOR\b", r"\bDNI/NIE DEL COMPRADOR\b",
        r"\bDIRECCIÓN DEL COMPRADOR\b", r"\bFECHA DEL CONTRATO\b", r"\b[A-Z\s]{3,}\b"
    ]

    for pattern in placeholders:
        match = re.search(pattern, text)
        if match:
            text = text[:match.start()].strip()
            break

    # Sustituir saltos de línea por espacios
    text = text.replace("\n", " ")

    # Evitar que la sugerencia esté completamente contenida en el texto existente
    normalized_existing = re.sub(r'\s+', ' ', existing_text.lower().strip())
    normalized_text = re.sub(r'\s+', ' ', text.lower().strip())

    # Eliminar duplicado al inicio
    if text.lower().startswith(existing_text.lower()):
        text = text[len(existing_text):].strip()
    if normalized_text in normalized_existing:
        return ""

    return text