# backend/models/legalchat.py

from generar_query_mistral import generar_query_juridica_mistral
from chatlegal_others.buscar_fragmentos import get_fragmentos_legales
from config import OPENROUTER_API_KEY
from openai import OpenAI
import os

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

def generate_legal_chat_response(messages):
    pregunta_usuario = messages[-1]["content"]
    modo_instruccion = next((m["content"] for m in messages if m["role"] == "system"), "")

    fragmentos = get_fragmentos_legales(pregunta_usuario) or []
    contexto = "\n\n".join(
        f"📘 **Ley:** {f['ley_id'].replace('_', ' ').title()}\n📝 {f['texto']}"
        for f in fragmentos if f
    )

    prompt = (
        f"{modo_instruccion}\n\n"
        f"Ten en cuenta los siguientes artículos legales:\n\n{contexto}\n\n"
        f"Ahora responde a la siguiente consulta de forma clara, explicativa y argumentada.\n"
        f"❓ Pregunta: {pregunta_usuario}"
    )

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=700
    )

    respuesta = response.choices[0].message.content.strip()

    # Añadir referencias legales y palabras clave
    referencias = [
        f"**{f['ley_id'].replace('_', ' ').title()}**. {f['texto'][:150]}..."
        for f in fragmentos if f
    ]

    if referencias:
        respuesta += "\n\n---\n\n📚 **Leyes citadas:**\n\n" + "\n\n".join(referencias)

    keywords = generar_query_juridica_mistral(pregunta_usuario)
    if keywords:
        respuesta += f"\n\n---\n\n🔎 **Palabras clave para buscar jurisprudencia:**\n{keywords}"

    return respuesta
