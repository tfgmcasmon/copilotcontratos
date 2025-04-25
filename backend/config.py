import json
import os

# Ruta al archivo secrets.json (ajusta si cambia de carpeta)
SECRETS_PATH = os.path.join(os.path.dirname(__file__), '..', 'secrets.json')

# Cargar API key de OpenRouter
with open(SECRETS_PATH, 'r', encoding='utf-8') as f:
    secrets = json.load(f)

OPENROUTER_API_KEY = secrets.get("openai_api_key")
