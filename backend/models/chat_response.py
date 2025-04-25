from openai import OpenAIError
from config import OPENROUTER_API_KEY
from openai import OpenAI
from services.chat_context_builder import build_chat_context

# Cliente para OpenRouter
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

def generate_chat_response(user_question):
    """
    Genera una respuesta jurídica a partir de una pregunta usando Mistral.
    """
    context = build_chat_context()

    prompt = f"{context}\n\nPregunta del usuario: {user_question}\n\nRespuesta:"  

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct:free",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )

    answer = response.choices[0].message.content.strip()
    return answer
