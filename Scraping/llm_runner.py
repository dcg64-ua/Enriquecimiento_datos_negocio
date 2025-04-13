import requests

def preguntar_al_llm(html, query):
    system_prompt = (
        "Eres un asistente que ayuda a extraer información útil de HTML. La respuesta debe ser muy precisa. "
        "Si no encuentras la respuesta, responde únicamente con: NO ENCONTRADO. "
        "Ten en cuenta que te iré pasando más HTMLs con diferentes niveles de profundidad. "
        "Si la respuesta no es perfecta, espera a más información en siguientes iteraciones. "
        "Por ejemplo, si la pregunta es sobre los ingredientes de una tarta, no digas 'crema' o 'galleta', "
        "espera a decir los ingredientes exactos como harina, leche, azúcar, etc."
    )

    prompt = f"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
Extrae la siguiente información del siguiente HTML:

Pregunta: {query}

HTML:
{html}
<|im_end|>
<|im_start|>assistant
"""

    try:
        response = requests.post(
            "http://localhost:1234/v1/completions",
            headers={"Content-Type": "application/json"},
            json={
                "prompt": prompt,
                "temperature": 0.2,
                "max_tokens": 4000,
                "stop": ["<|im_end|>"],
                "model": "qwen2.5-7b-instruct-1m"
            },
            timeout=60  # Evitar cuelgues largos
        )
        response.raise_for_status()
        return response.json()["choices"][0]["text"].strip()
    except (requests.exceptions.RequestException, KeyError) as e:
        print("❌ Error al procesar la respuesta del modelo:", e)
        print("Respuesta bruta:", response.text if 'response' in locals() else "No se recibió respuesta.")
        return "NO ENCONTRADO"
