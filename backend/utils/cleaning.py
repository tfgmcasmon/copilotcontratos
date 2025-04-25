import re

def clean_and_cut_autocomplete(text, existing_text, is_first_completion):
    text = text.strip()

    # Evita repetir el título
    if is_first_completion:
        normalized_title = re.sub(r'[^a-zA-Z0-9]', '', existing_text.lower())
        normalized_text = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
        if normalized_text.startswith(normalized_title):
            text = text[len(existing_text):].strip()

    # Elimina placeholders
    placeholders = [
        r"\[.*?\]", r"\(.*?\)", r"\{.*?\}", r"XXXX+", r"DNI:\s*X{6,10}",
        r"DNI/NIE:\s*_+", r"Dirección:\s*_+", r"Fecha:\s*\d{0,2}/\d{0,2}/\d{0,4}",
        r"_{2,}", r"\.\.\.", r'" "', r"\s*_\s*"
    ]
    for pattern in placeholders:
        match = re.search(pattern, text)
        if match:
            text = text[:match.start()].strip()
            break

    # Evita duplicados
    normalized_existing = re.sub(r'\s+', ' ', existing_text.lower().strip())
    normalized_text = re.sub(r'\s+', ' ', text.lower().strip())
    if normalized_text in normalized_existing:
        return ""

    return text
