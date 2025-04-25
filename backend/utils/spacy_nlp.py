import spacy

# Cargamos el modelo de SpaCy solo una vez para toda la aplicación
# (puedes cambiar a 'es_core_news_md' si quieres usar uno más grande)
nlp = spacy.load("es_core_news_md")
