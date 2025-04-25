# gestor_tareas/llm_routing.py
from openai import OpenAI
import os, json

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=json.load(open(os.path.join(os.path.dirname(__file__), '../..', 'secrets.json')))["openai_api_key"]
)

def analizar_tarea_con_llm(titulo, descripcion, tipo, urgencia):
    prompt = f"""
Eres un asistente experto en gestión de tareas legales en derecho inmobiliario y mercantil. 
Una nueva tarea ha sido creada con estos datos:

Título: {titulo}
Tipo general: {tipo}
Descripción: {descripcion}
Urgencia: {urgencia}

Devuelve en JSON las siguientes claves:
- fases (lista de subtareas)
- responsables_por_fase (junior/intermedio/socia)
- prioridad_numérica (int de 0-100)
- observaciones_adicionales (breve texto)
"""
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.4
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("❌ Error al usar LLM:", e)
        return None
