import json
import os

def buscar_articulos_relevantes(texto_usuario, contract_type="general"):
    ruta = os.path.join(os.path.dirname(__file__), "..", "data", "leyes.json")

    with open(ruta, "r", encoding="utf-8") as f:
        leyes = json.load(f)

    relevantes = []
    palabras_clave = texto_usuario.lower().split()

    for ley in leyes:
        texto_articulo = (ley["texto"] + " " + ley["articulo"]).lower()
        if any(palabra in texto_articulo for palabra in palabras_clave):
            relevantes.append(f"Artículo {ley['articulo']} ({ley['ley']}): {ley['texto']}")

    # Devolver máximo 3 artículos para no saturar
    return "\n".join(relevantes[:3]) if relevantes else "No se encontraron artículos relevantes."

