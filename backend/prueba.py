from chatlegal_others.buscar_jurisprudencia_boe import buscar_sentencias_boe

# Simulamos una pregunta legal
consulta_usuario = "¿Si mi hijo me maltrata puedo desheredarlo?"

# Puedes reutilizar tus keywords generadas con Mistral aquí directamente
keywords = "desheredación maltrato filiación legítima violencia doméstica"

# Ejecutamos la búsqueda en el BOE
resultados = buscar_sentencias_boe(keywords)

# Mostramos resultados
if resultados:
    print("📚 Casos prácticos encontrados:\n")
    for res in resultados:
        print(f"📘 {res['titulo']}")
        print(f"📝 {res['resumen']}")
        print(f"🔗 {res['url']}")
        print("-" * 100)
else:
    print("❌ No se encontraron sentencias relevantes.")
