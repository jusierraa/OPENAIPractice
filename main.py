import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar API key desde el archivo .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Configurar parámetros del modelo:
#model: el modelo que vas a usar
#temperature: qué tan creativa o variable será la respuesta
#top_p: otra forma de controlar variedad
#frequency_penalty: evita repetir demasiado
#presence_penalty: incentiva introducir ideas nuevas

def set_open_params(
    model="gpt-4o-mini",
    ##model="GPT-3.5",
    temperature=0.7,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
):
    """ set openai parameters"""

    openai_params = {}

    openai_params['model'] = model
    openai_params['temperature'] = temperature
    openai_params['top_p'] = top_p
    openai_params['frequency_penalty'] = frequency_penalty
    openai_params['presence_penalty'] = presence_penalty
    return openai_params

def get_completion(params, messages):
    """ GET completion from openai api"""

    response = client.chat.completions.create(
        model = params['model'],
        messages = messages,
        temperature = params['temperature'],
        top_p = params['top_p'],
        frequency_penalty = params['frequency_penalty'],
        presence_penalty = params['presence_penalty'],
    )
    return response

params = set_open_params()

prompt = "La tierra es"

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

response = get_completion(params, messages)

print(response.choices[0].message.content)
