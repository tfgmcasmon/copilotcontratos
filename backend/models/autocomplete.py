from openai import OpenAIError
from config import OPENROUTER_API_KEY
from openai import OpenAI
from services.contract_context import get_contract_context
from services.text_cleaner import clean_and_cut_autocomplete

# Cliente para OpenRouter
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

# Variable auxiliar para control de títulos generados
last_generated_title = ""

def generate_autocomplete(user_text, contract_type):
    global last_generated_title

    context = get_contract_context(contract_type)

    prompt = f"{context} Continúa el siguiente texto, evitando placeholders y repeticiones: {user_text}"

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0.2
    )

    completion = response.choices[0].message.content.strip()

    is_first_completion = user_text == "" or last_generated_title in user_text

    cleaned_completion = clean_and_cut_autocomplete(completion, user_text, is_first_completion)

    if is_first_completion and cleaned_completion:
        last_generated_title = cleaned_completion.split("\n")[0]

    return cleaned_completion