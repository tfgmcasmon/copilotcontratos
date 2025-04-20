# gestor_tareas/nlp_task_analysis.py

import spacy

# Carga del modelo de lenguaje en español
nlp = spacy.load("es_core_news_sm")

CATEGORIAS_CLAVE = {
    "firma": ["firmar", "notaría", "documentos finales", "escritura"],
    "traduccion": ["traducción", "idioma", "versión en inglés"],
    "revisión": ["revisar", "verificar", "corregir", "comprobar"],
    "negociacion": ["negociar", "acuerdo", "condiciones"],
    "urgente": ["urgente", "plazo crítico", "entrega rápida"]
}

def analizar_tarea(descripcion):
    doc = nlp(descripcion)
    tokens = [t.text.lower() for t in doc if not t.is_stop and not t.is_punct]

    categorias_detectadas = set()
    for categoria, palabras in CATEGORIAS_CLAVE.items():
        if any(palabra in tokens for palabra in palabras):
            categorias_detectadas.add(categoria)

    entidades = [ent.text for ent in doc.ents]
    return list(categorias_detectadas), entidades


def clasificar_especialidad(categorias_detectadas):
    if "traduccion" in categorias_detectadas:
        return "internacional"
    elif "negociacion" in categorias_detectadas:
        return "mercantil"
    elif "firma" in categorias_detectadas:
        return "notarial"
    return "general"


def generar_explicacion_asignacion(tarea, usuario):
    return f"Asignada a {usuario.nombre} por carga baja ({usuario.carga}), rol {usuario.rol}, y experiencia adecuada para '{tarea.categoria_nlp if hasattr(tarea, 'categoria_nlp') else 'tarea general'}'."
