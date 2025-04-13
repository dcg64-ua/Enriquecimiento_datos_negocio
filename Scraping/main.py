# main.py
import argparse
import json
from extractor import run_scraper
from kml_parser import parse_kml
from llm_runner import preguntar_al_llm
from llm_ranker import rank_urls_por_relevancia

def dividir_en_bloques(lista, tam_bloque):
    return [lista[i:i + tam_bloque] for i in range(0, len(lista), tam_bloque)]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--kml', required=True)
    parser.add_argument('--query', required=True)
    parser.add_argument('--db', required=True)
    parser.add_argument('--deep', type=int, default=3)
    args = parser.parse_args()

    # Paso 1: Scraping
    urls = parse_kml(args.kml)
    run_scraper(urls, args.query, args.db, args.deep)

    # Paso 2: Cargar los resultados
    with open(args.db, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Paso 3: Rankear por bloques
    bloques = dividir_en_bloques(data, tam_bloque=10)
    candidatos = []

    for bloque in bloques:
        urls_bloque = [entrada["url"] for entrada in bloque]
        try:
            orden = rank_urls_por_relevancia(args.query, urls_bloque)
            top_3_indices = orden[:3]
            candidatos.extend([bloque[i] for i in top_3_indices])
        except Exception as e:
            print(f"⚠️ Error al ordenar un bloque: {e}")

    # Re-rankear candidatos finales
    urls_finales = [entrada["url"] for entrada in candidatos]
    try:
        orden_final = rank_urls_por_relevancia(args.query, urls_finales)
        ordenadas = [candidatos[i] for i in orden_final]
    except Exception as e:
        print(f"⚠️ Error al reordenar candidatos finales: {e}")
        ordenadas = candidatos

    # Paso 4: Consultar al LLM
    for entrada in ordenadas:
        url = entrada["url"]
        html = entrada["html"]

        print(f"\nConsultando al LLM: {url}\n")
        respuesta = preguntar_al_llm(html, args.query)

        if "NO ENCONTRADO" not in respuesta.upper() and respuesta.strip() != "":
            print(f"\n✅ Información encontrada en: {url}\n")
            print(f"📄 Respuesta: {respuesta.strip()}")
            break