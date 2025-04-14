import json
import faiss
from sentence_transformers import SentenceTransformer
from collections import defaultdict

INDEX_PATH = "data/faiss_index.bin"
META_PATH = "data/fragmentos_metadata.json"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def cargar_modelo():
    return SentenceTransformer(MODEL_NAME)

def cargar_index():
    return faiss.read_index(INDEX_PATH)

def cargar_metadatos():
    with open(META_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def buscar_pregunta(pregunta, modelo, index, metadatos, top_k=5):
    embedding = modelo.encode([pregunta])
    _, indices = index.search(embedding, top_k)

    resultados = []
    for i in indices[0]:
        fragmento = metadatos[i]
        resultados.append(fragmento)

    return resultados

def recuperar_fragmentos(query, index, metadata, padding=100):
    """
    Devuelve los fragmentos más relevantes con algo de contexto (padding).
    """
    D, I = index.search(query_vector, k=5)
    fragmentos_recuperados = []

    for idx in I[0]:
        if idx >= len(metadata): continue
        info = metadata[idx]

        start = max(0, info["start"] - padding)
        end = info["end"] + padding

        with open("data/boe_ley_fragmentada.json", "r", encoding="utf-8") as f:
            ley_fragmentada = json.load(f)

        fragmento = ley_fragmentada[info["ley_id"]][start:end]
        fragmentos_recuperados.append({
            "texto": fragmento,
            "ley_id": info["ley_id"],
            "articulo": info.get("articulo_id", "desconocido")
        })

    return fragmentos_recuperados


def main():
    pregunta = input(" Pregunta legal en lenguaje natural: ").strip()

    print("Buscando fragmentos relevantes...\n")
    modelo = cargar_modelo()
    index = cargar_index()
    metadatos = cargar_metadatos()

    resultados = buscar_pregunta(pregunta, modelo, index, metadatos)

    for r in resultados:
        print(f" Ley: {r['ley']}, Artículo ID: {r['id']}\n {r['texto']}\n" + "-"*80)

if __name__ == "__main__":
    main()
