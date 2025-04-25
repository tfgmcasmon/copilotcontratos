import requests
import json
import os

with open(os.path.join(os.path.dirname(__file__), '..', 'secrets.json'), 'r', encoding='utf-8') as f:
    secrets = json.load(f)

print("🔐 Clave API:", secrets.get("openai_api_key"))  # TEMPORAL para ver si se carga
headers = {
    "Authorization":f"Bearer {secrets['openai_api_key']}",
    "Content-Type": "application/json"
}

data = {
    "model": "mistralai/mistral-7b-instruct",
    "messages": [{"role": "user", "content": "¿Qué es el usufructo?"}],
    "temperature": 0.5,
    "max_tokens": 100
}

response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
print(response.status_code)
print(response.json())
