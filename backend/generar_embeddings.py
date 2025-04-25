import os
import json
import glob
from tqdm import tqdm
import faiss
from sentence_transformers import SentenceTransformer

# Rutas
FRAGMENTOS_DIR = "data/fragmentos"
OUTPUT_INDEX = "data/faiss_index.bin"
OUTPUT_META = "data/fragmentos_metadata.json"

# Modelo
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def cargar_fragmentos():
    fragmentos = []
    metadatos = []
    for ruta in glob.glob(os.path.join(FRAGMENTOS_DIR, "*.json")):
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
            for item in datos:
                fragmentos.append(item["texto"])
                metadatos.append({
                    "ley": os.path.basename(ruta).replace(".json", ""),  # Ley
                    "ley_id": item["ley_id"],  # Identificador de la ley
                    "articulo": item["articulo"],  # Artículo
                    "texto": item["texto"][:200] + "..."  # Previo al texto
                })
    return fragmentos, metadatos

def generar_embeddings(textos, modelo):
    return modelo.encode(textos, show_progress_bar=True, convert_to_numpy=True)

def guardar_faiss_index(embeddings, metadatos):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, OUTPUT_INDEX)

    with open(OUTPUT_META, "w", encoding="utf-8") as f:
        json.dump(metadatos, f, ensure_ascii=False, indent=2)

def main():
    print("📚 Cargando fragmentos legales...")
    textos, metadatos = cargar_fragmentos()

    print(f"✍️ Fragmentos cargados: {len(textos)}")

    print("🔎 Generando embeddings...")
    modelo = SentenceTransformer(MODEL_NAME)
    embeddings = generar_embeddings(textos, modelo)

    print("💾 Guardando índice FAISS y metadatos...")
    guardar_faiss_index(embeddings, metadatos)

    print("✅ Embeddings e índice guardados correctamente.")

if __name__ == "__main__":
    main()
