import requests
from bs4 import BeautifulSoup
import json
import re
import os

INPUT_JSON = "data/boe_codigos_consolidados.json"
OUTPUT_DIR = "data/fragmentos"

def get_boe_html(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error al acceder a {url}")

def extract_articles(html, ley_id):
    soup = BeautifulSoup(html, 'lxml')
    content_div = soup.find('div', {'id': 'contenido'})  # donde está el texto real
    if not content_div:
        raise Exception("No se encontró el contenido legal principal")

    articles = []
    current_article = ""
    current_articulo_id = None

    # Recorremos el contenido en busca de artículos y extraemos texto
    for tag in content_div.find_all(["p", "h3", "h4", "h5"]):
        text = tag.get_text().strip()

        # Si encontramos un artículo
        if re.match(r"^Artículo\s+\d+[\.º]?", text):
            # Guardamos el artículo anterior, si existe
            if current_article:
                articles.append({
                    "texto": current_article.strip(),
                    "ley_id": ley_id,
                    "articulo": current_articulo_id
                })
            current_article = text
            current_articulo_id = text.split()[1]  # Extraemos el número del artículo
        elif current_article:
            current_article += "\n" + text

    # Añadimos el último artículo encontrado
    if current_article:
        articles.append({
            "texto": current_article.strip(),
            "ley_id": ley_id,
            "articulo": current_articulo_id
        })

    return articles

def guardar_fragmentos(nombre_archivo, fragmentos):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ruta = os.path.join(OUTPUT_DIR, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(fragmentos, f, ensure_ascii=False, indent=2)

def slugify(texto):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', texto.lower())[:50]

def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        leyes = json.load(f)

    for ley in leyes:
        print(f"📄 Procesando: {ley['title']}")
        try:
            html = get_boe_html(ley["url"])
            fragmentos = extract_articles(html, ley["title"])  # Pasamos la ley como ID
            archivo_salida = slugify(ley["title"]) + ".json"
            guardar_fragmentos(archivo_salida, fragmentos)
            print(f"✅ Guardado: {archivo_salida} ({len(fragmentos)} artículos)")
        except Exception as e:
            print(f"❌ Error en {ley['title']}: {e}")

if __name__ == "__main__":
    main()
