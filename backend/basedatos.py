import requests
from bs4 import BeautifulSoup
import json
import re
import os

# URL del texto consolidado REAL (versión con todos los artículos visibles)
URL = "https://www.boe.es/buscar/act.php?id=BOE-A-2013-12913&tn=1&p=20230614"

def get_boe_html(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error al acceder a {url}")

def extract_articles(html):
    soup = BeautifulSoup(html, 'lxml')

    content_div = soup.find('div', {'id': 'contenido'})  # el bueno
    if not content_div:
        raise Exception("No se encontró el contenido legal principal")

    articles = []
    current_article = ""

    for tag in content_div.find_all(["p", "h3", "h4", "h5"]):
        text = tag.get_text().strip()

        # Detectar artículo
        if re.match(r"^Artículo\s+\d+[\.º]?", text):
            if current_article:
                articles.append(current_article.strip())
            current_article = text
        elif current_article:
            current_article += "\n" + text

    if current_article:
        articles.append(current_article.strip())

    return articles

def save_fragments_to_json(fragments, filename="boe_ley_fragmentada.json"):
    os.makedirs("data", exist_ok=True)
    with open(os.path.join("data", filename), "w", encoding="utf-8") as f:
        json.dump([{"id": i, "texto": frag} for i, frag in enumerate(fragments)], f, ensure_ascii=False, indent=2)

def main():
    html = get_boe_html(URL)
    fragments = extract_articles(html)
    save_fragments_to_json(fragments)
    print(f"✅ Guardados {len(fragments)} artículos legales reales en 'data/boe_ley_fragmentada.json'")

if __name__ == "__main__":
    main()
