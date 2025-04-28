import re
from utils.spacy_nlp import nlp


def anonymize_text(text):
    replacements = {}
    doc = nlp(text)

    # Reemplazar entidades de personas, localizaciones y organizaciones
    for ent in doc.ents:
        if ent.label_ in ["PER", "LOC", "ORG"]:
            key = f"<{ent.label_}{len(replacements)}>"
            replacements[key] = ent.text
            text = text.replace(ent.text, key)

    # Reemplazar DNIs
    text = replace_pattern(text, r'\b\d{8}[A-Z]\b', "DNI", replacements)

    # Reemplazar teléfonos
    text = replace_pattern(text, r'\b(6|7)\d{8}\b', "TELEFONO", replacements)

    return text, replacements


def revert_replacements(text, replacements):
    if not replacements:
        return text

    # Ordenar para reemplazar primero los más largos (por seguridad)
    sorted_replacements = sorted(replacements.items(), key=lambda x: -len(x[0]))

    # Construir patrón regex
    pattern = re.compile("|".join(re.escape(k) for k, _ in sorted_replacements))

    # Función de reemplazo segura
    def substitute(match):
        return replacements.get(match.group(0), match.group(0))

    # Aplicar reemplazo atómico
    reverted_text = pattern.sub(substitute, text)

    return reverted_text



def replace_pattern(text, pattern, label, replacements):
    matches = re.findall(pattern, text)
    for match in matches:
        key = f"<{label}{len(replacements)}>"
        replacements[key] = match
        text = text.replace(match, key)
    return text