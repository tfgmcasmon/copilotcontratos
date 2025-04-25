import re
from collections import defaultdict
from utils.spacy_nlp import nlp

def verify_contract_data(contract_text):
    issues = []

    doc = nlp(contract_text)

    person_data = {}  # persona -> datos asociados
    global_dnis = {}
    global_telefonos = defaultdict(set)

    for sent in doc.sents:
        sentence = sent.text
        sent_doc = nlp(sentence)
        nombres = [ent.text.strip() for ent in sent_doc.ents if ent.label_ == "PER"]

        if not nombres:
            continue

        posibles_dnis = re.findall(r'\b\d{7,8}[A-Za-z]\b', sentence)
        telefonos = re.findall(r'\b6\d{8}\b|\b7\d{8}\b', sentence)

        for nombre in nombres:
            nombre_key = nombre.lower()
            if nombre_key not in person_data:
                person_data[nombre_key] = {
                    "nombre_original": nombre,
                    "dnis": set(),
                    "telefonos": set()
                }

            for dni in posibles_dnis:
                person_data[nombre_key]["dnis"].add(dni.upper())

            for tel in telefonos:
                person_data[nombre_key]["telefonos"].add(tel)
                global_telefonos[tel].add(nombre_key)

    for persona, datos in person_data.items():
        nombre = datos["nombre_original"]

        if len(datos["dnis"]) > 1:
            issues.append(f"❌ '{nombre}' tiene múltiples DNIs: {', '.join(datos['dnis'])}")

        for dni in datos["dnis"]:
            if dni in global_dnis and global_dnis[dni] != persona:
                otra = person_data[global_dnis[dni]]["nombre_original"]
                issues.append(f"❌ DNI '{dni}' está asociado a múltiples personas: '{nombre}' y '{otra}'")
            else:
                global_dnis[dni] = persona

        for tel in datos["telefonos"]:
            if len(global_telefonos[tel]) > 1:
                personas_con_tel = [person_data[p]["nombre_original"] for p in global_telefonos[tel]]
                issues.append(f"❌ El teléfono '{tel}' está siendo usado por múltiples personas: {', '.join(personas_con_tel)}.")

    return issues