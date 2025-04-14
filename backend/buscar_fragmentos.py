import json
import faiss
from sentence_transformers import SentenceTransformer
from collections import defaultdict

INDEX_PATH = "data/faiss_index.bin"
META_PATH = "data/fragmentos_metadata.json"
LEYES_PATH = "data/boe_ley_fragmentada.json"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def cargar_modelo():
    return SentenceTransformer(MODEL_NAME)

def cargar_index():
    return faiss.read_index(INDEX_PATH)

def cargar_metadatos():
    with open(META_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_leyes():
    with open(LEYES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def recuperar_fragmentos(query_vector, index, metadata, leyes, padding=100, k=5):
    D, I = index.search(query_vector, k)
    fragmentos_recuperados = []

    for idx in I[0]:
        if idx >= len(metadata): continue
        info = metadata[idx]

        start = max(0, info["start"] - padding)
        end = info["end"] + padding

        ley_id = info["ley_id"]
        fragmento = leyes[ley_id][start:end]

        fragmentos_recuperados.append({
            "texto": fragmento,
            "ley_id": ley_id,
            "articulo": info.get("articulo_id", "desconocido")
        })

    return fragmentos_recuperados

def agrupar_por_articulo(fragmentos):
    articulos = defaultdict(str)

    for frag in fragmentos:
        key = (frag["ley_id"], frag["articulo"])
        articulos[key] += frag["texto"].strip() + " "

    return [{"ley_id": k[0], "articulo": k[1], "texto": v.strip()} for k, v in articulos.items()]

def limitar_longitud(fragmentos, max_tokens=1500):
    total = 0
    seleccionados = []

    for frag in fragmentos:
        tokens = len(frag["texto"].split())
        if total + tokens > max_tokens:
            break
        seleccionados.append(frag)
        total += tokens

    return seleccionados

def get_fragmentos_legales(pregunta, k=5, max_tokens=1200, padding=100):
    modelo = cargar_modelo()
    index = cargar_index()
    metadatos = cargar_metadatos()

    vector = modelo.encode([pregunta])
    D, I = index.search(vector, k)

    with open("data/boe_ley_fragmentada.json", "r", encoding="utf-8") as f:
        texto_fragmentado = json.load(f)

    fragmentos_raw = []
    for idx in I[0]:
        if idx >= len(metadatos):
            continue
        meta = metadatos[idx]

        ley_id = meta.get("ley_id", "desconocida")
        articulo = meta.get("articulo_id", "desconocido")

        if "start" in meta and "end" in meta:
            start = max(0, meta["start"] - padding)
            end = meta["end"] + padding
            texto = texto_fragmentado.get(ley_id, "")[start:end]
        else:
            texto = meta.get("texto", "")

        fragmentos_raw.append({
            "ley_id": ley_id,
            "articulo": articulo,
            "texto": texto.strip()
        })

    return limitar_longitud(fragmentos_raw, max_tokens=max_tokens)

def main():
    pregunta = input("❓ Pregunta legal en lenguaje natural: ").strip()
    print("🔍 Buscando fragmentos relevantes...\n")

    resultados = get_fragmentos_legales(pregunta)

    for r in resultados:
        print(f"📘 Ley: {r['ley_id']}, Artículo: {r['articulo']}\n📝 {r['texto']}\n" + "-"*80)

if __name__ == "__main__":
    main()
