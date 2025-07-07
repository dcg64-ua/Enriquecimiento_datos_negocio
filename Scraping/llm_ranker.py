import requests
import time

def rank_urls_por_relevancia(query, urls, modelo="qwen2.5-7b-instruct", bloque=10, max_reintentos=3):
    indices_ordenados = []

    for i in range(0, len(urls), bloque):
        urls_bloque = urls[i:i + bloque]
        intentos = 0
        indices_relativos = None

        while intentos < max_reintentos:
            prompt = (
                "Dada la siguiente pregunta, ordena estas URLs según la probabilidad de que "
                "contengan la información solicitada, de mayor a menor. "
                "Devuélveme ÚNICAMENTE una lista de índices RELATIVOS AL BLOQUE como esta: [1, 0, 2, 5, 4, 3, 6, 8, 9, 7], la lista tendrá"
                "entre 1 y 10 elementos, en la lista coloca el mismo numero de elementos que URLs hay en el bloque, "
                "NO EXPLIQUES NADA. SOLO devuelve la lista, sin ningún otro texto. \n\n"
                f"Pregunta: {query}\n\n"
                "URLs:\n"
            )

            for j, url in enumerate(urls_bloque):
                prompt += f"{j}: {url}\n"

            prompt += "\nRecuerda: ORDENA TODAS las URLs por relevancia. NO OMITAS NINGUNA. SOLO la lista. PASAME SOLO LA LISTA NINGUNA EXPLICACION POR FAVOR"

            print(prompt)
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
                print(f"🔁 Intento {intentos + 1} del bloque {i}-{i + bloque}")
                print("🔎 DEBUG respuesta del ranker:\n", respuesta)

                texto = respuesta["choices"][0]["text"].strip()
                texto = texto.splitlines()[-1].strip()

                if texto.startswith("[") and texto.endswith("]"):
                    indices_relativos = eval(texto)
                    if (
                        isinstance(indices_relativos, list)
                        and set(indices_relativos) == set(range(len(urls_bloque)))
                    ):
                        break  # ¡Éxito!
                    else:
                        raise ValueError("La lista no tiene todos los índices esperados")
                else:
                    raise ValueError("Formato inválido")

            except Exception as e:
                print(f"⚠️ Error al procesar el bloque {i}-{i + bloque}: {e}")
                intentos += 1
                time.sleep(1)

        if indices_relativos is not None:
            indices_absolutos = [i + j for j in indices_relativos]
            indices_ordenados.extend(indices_absolutos)
        else:
            print(f"❌ Se alcanzó el máximo de reintentos para el bloque {i}-{i + bloque}")

    return indices_ordenados
