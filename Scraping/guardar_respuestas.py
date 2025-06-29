import json
import os

RESPUESTAS_PATH = "respuestas.json"

def guardar_respuesta(url, pregunta, respuesta):
    nueva = {
        "url": url,
        "pregunta": pregunta,
        "respuesta": respuesta.strip()
    }

    # Si el archivo ya existe, lo cargamos
    if os.path.exists(RESPUESTAS_PATH):
        with open(RESPUESTAS_PATH, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = []
    else:
        datos = []

    # Añadir nueva entrada
    datos.append(nueva)

    # Guardar de nuevo el archivo
    with open(RESPUESTAS_PATH, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
