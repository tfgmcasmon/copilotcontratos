# buscar_jurisprudencia.py

import urllib.parse

def generar_enlace_cgpj(keywords):
    """
    Devuelve un enlace directo al buscador del CGPJ con las palabras clave dadas.

    Parameters:
        keywords (str): Palabras clave separadas por espacios.

    Returns:
        str: URL lista para usar en el navegador.
    """
    query = "+".join(keywords.strip().split())
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.poderjudicial.es/search/indexAN.jsp?tipoBusqueda=palabra&contenido={encoded_query}"
