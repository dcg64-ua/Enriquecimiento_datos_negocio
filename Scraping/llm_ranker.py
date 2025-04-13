# llm_ranker.py
import requests

def rank_urls_por_relevancia(query, urls, modelo="qwen2.5-7b-instruct", bloque=10):
    indices_ordenados = []

    for i in range(0, len(urls), bloque):
        urls_bloque = urls[i:i+bloque]
        prompt = (
            "Dada la siguiente pregunta, ordena estas URLs según la probabilidad de que "
            "contengan la información solicitada, de mayor a menor. "
            "Devuélveme ÚNICAMENTE una lista de índices RELATIVOS AL BLOQUE como esta: [1, 0, 2]. "
            "NO EXPLIQUES NADA. SOLO devuelve la lista, sin ningún otro texto. \n\n"
            f"Pregunta: {query}\n\n"
            "URLs:\n"
        )

        for j, url in enumerate(urls_bloque):
            prompt += f"{j}: {url}\n"

        prompt += "\nRecuerda: ORDENA TODAS las URLs por relevancia. NO OMITAS NINGUNA. SOLO la lista. PASAME SOLO LA LISTA NINGUNA EXPLICACION POR FAVOR"

        try:
            response = requests.post(
                "http://localhost:1234/v1/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "prompt": prompt,
                    "temperature": 0,
                    "max_tokens": 1000,
                    "stop": None,
                    "model": "qwen2.5-7b-instruct-1m"
                }
            )
            respuesta = response.json()
            print("🔎 DEBUG respuesta del ranker:\n", respuesta)

            texto = respuesta["choices"][0]["text"].strip()
            if texto == "":
                raise ValueError("Respuesta vacía del modelo")

            texto = texto.splitlines()[-1].strip()
            if texto.startswith("[") and texto.endswith("]"):
                indices_relativos = eval(texto)
                if isinstance(indices_relativos, list):
                    indices_absolutos = [i + j for j in indices_relativos]
                    indices_ordenados.extend(indices_absolutos)
                else:
                    raise ValueError("Respuesta no es una lista")
            else:
                raise ValueError("Respuesta no tiene formato de lista")

        except Exception as e:
            print(f"⚠️ Error al procesar bloque {i}-{i+bloque}: {e}")

    return indices_ordenados
