import re

def clean_and_cut_autocomplete(text, existing_text, is_first_completion):

    # Quita espacios extra y normaliza
    text = text.strip()

    # Evita repetir lo ya escrito
    if text.lower().startswith(existing_text.lower()):
        text = text[len(existing_text):].strip()

    # Quita placeholders genéricos y títulos repetidos
    placeholders = [
        r"\[.*?\]", r"\(.*?\)", r"\{.*?\}",
        r"XXXX+", r"NOMBRE", r"DNI", r"[A-Z\s]{4,}", r"_{2,}", r"\.\.\."
    ]
    for pattern in placeholders:
        match = re.search(pattern, text)
        if match:
            text = text[:match.start()].strip()
            break

    # Reemplaza múltiples saltos de línea por solo uno
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text
