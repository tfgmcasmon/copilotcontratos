import requests
from bs4 import BeautifulSoup

def buscar_sentencias_boe(keywords, max_resultados=5):
    """
    Busca resoluciones judiciales en el BOE utilizando palabras clave.
    Devuelve una lista con título, resumen y enlace de los resultados.
    """
    base_url = "https://www.boe.es/buscar/boe.php"
    query = "+".join(keywords.split())
    params = {"n": "10", "tn": "SENTENCIA", "q": keywords}


    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error al conectar con el BOE: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    resultados = []

    for li in soup.select("li.resultado-busqueda")[:max_resultados]:
        titulo_tag = li.find("a")
        resumen_tag = li.find("p", class_="resultado-resumen")
        if not titulo_tag:
            continue

        resultados.append({
            "titulo": titulo_tag.get_text(strip=True),
            "resumen": resumen_tag.get_text(strip=True) if resumen_tag else "",
            "url": f"https://www.boe.es{titulo_tag['href']}"
        })

    return resultados


# Prueba manual
if __name__ == "__main__":
    consulta = "maltrato desheredación herencia"
    resultados = buscar_sentencias_boe(consulta)
    for res in resultados:
        print(f"\n📘 {res['titulo']}\n📝 {res['resumen']}\n🔗 {res['url']}\n{'-'*80}")
