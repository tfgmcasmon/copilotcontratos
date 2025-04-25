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
    for placeholder, original_value in replacements.items():
        text = text.replace(placeholder, original_value)
    return text


def replace_pattern(text, pattern, label, replacements):
    matches = re.findall(pattern, text)
    for match in matches:
        key = f"<{label}{len(replacements)}>"
        replacements[key] = match
        text = text.replace(match, key)
    return text