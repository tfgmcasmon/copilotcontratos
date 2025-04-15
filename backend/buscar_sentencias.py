# buscar_jurisprudencia.py
import requests
from bs4 import BeautifulSoup

def buscar_sentencias_cgpj(keywords):
    """
    Realiza una búsqueda en www.poderjudicial.es con palabras clave.
    Devuelve una lista de títulos y enlaces.
    """
    base_url = "https://www.poderjudicial.es/search/indexAN.jsp"
    query = "+".join(keywords.split())
    params = {"tipoBusqueda": "palabra", "contenido": query}

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error al conectar con CGPJ: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    print(soup.prettify()[:1500])  # te muestra los primeros 1500 caracteres del HTML
    resultados = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        texto = link.get_text(strip=True)
        if "documento" in href and texto:
            full_url = f"https://www.poderjudicial.es{href}"
            resultados.append({"titulo": texto, "url": full_url})
        if len(resultados) >= 5:
            break

    return resultados
