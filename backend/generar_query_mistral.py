import json
from openai import OpenAI
import os

# Cargar tu API key
with open(os.path.join(os.path.dirname(__file__), '..', 'secrets.json'), 'r', encoding='utf-8') as file:
    SECRETS = json.load(file)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=SECRETS["openai_api_key"],
)

def generar_query_juridica_mistral(pregunta_usuario):
    """
    Usa Mistral para transformar una pregunta legal en una búsqueda de palabras clave jurídicas.
    """
    system_prompt = (
        "Transforma la siguiente consulta legal en una búsqueda jurídica breve y relevante, "
        "usando solo palabras clave legales (tipo: herencia, maltrato, custodia, desheredación, etc). "
        "No repitas la pregunta. Solo responde con las palabras clave separadas por espacios."
    )

    user_prompt = f"Consulta: {pregunta_usuario}"

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=30
        )

        keywords = response.choices[0].message.content.strip()
        return keywords

    except Exception as e:
        print(f"❌ Error generando búsqueda: {e}")
        return ""
