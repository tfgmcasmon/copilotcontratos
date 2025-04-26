import re

def detectar_incompletos(text):
    placeholders = ["XXXX", "NOMBRE", "DNI", "________", "..."]
    return [p for p in placeholders if p in text]

def detectar_articulos_legales(text):
    return re.findall(r"art[ií]culo\s+\d{1,4}", text, flags=re.IGNORECASE)

def detectar_secciones_clave(text):
    claves = ["cláusula 1", "identificación", "objeto", "precio", "plazo", "firma"]
    return [s for s in claves if s.lower() in text.lower()]

def preanalisis_estructural(text):
    return {
        "placeholders_detectados": detectar_incompletos(text),
        "articulos_legales": detectar_articulos_legales(text),
        "secciones_clave": detectar_secciones_clave(text)
    }
