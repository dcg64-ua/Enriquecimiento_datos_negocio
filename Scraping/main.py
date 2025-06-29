# main.py
import argparse
import json
from extractor import run_scraper
from kml_parser import parse_kml
from llm_runner import preguntar_al_llm
from llm_ranker import rank_urls_por_relevancia
from urllib.parse import urlparse
from collections import defaultdict
from guardar_respuestas import guardar_respuesta


def dividir_en_bloques(lista, tam_bloque):
    return [lista[i:i + tam_bloque] for i in range(0, len(lista), tam_bloque)]

def agrupar_por_raiz(data):
    grupos = defaultdict(list)
    for entrada in data:
        dominio = urlparse(entrada["url"]).netloc
        grupos[dominio].append(entrada)
    return grupos

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--kml', required=True)
    parser.add_argument('--query', required=True)
    parser.add_argument('--db', required=True)
    parser.add_argument('--deep', type=int, default=3)
    args = parser.parse_args()

    # Paso 1: Scraping
    urls = parse_kml(args.kml)
    print(f"🔗 URLs extraídas del KML: {len(urls)} URLs encontradas.")
    print (f"🔗 URLs: {urls}")
    run_scraper(urls, args.query, args.db, args.deep)

    print(f"✅ Scraping completado. Resultados guardados en {args.db}")
    

    # Paso 2: Cargar los resultados
    with open(args.db, "r", encoding="utf-8") as f:
        data = json.load(f)

    grupos = agrupar_por_raiz(data)
    for dominio, grupo in grupos.items():
        print(f"\n🌐 Procesando dominio: {dominio} con {len(grupo)} URLs")

        # Paso 3: Rankear por bloques
        bloques = dividir_en_bloques(grupo, tam_bloque=10)
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


        representativa = grupo[0]
        if all(representativa["url"] != entrada["url"] for entrada in ordenadas):
            ordenadas.append(representativa)

        # Paso 4: Consultar al LLM
        for entrada in ordenadas:
            url = entrada["url"]
            html = entrada["html"]

            print(f"\nConsultando al LLM: {url}\n")
            respuesta = preguntar_al_llm(html, args.query)

            if "NO ENCONTRADO" not in respuesta.upper() and respuesta.strip() != "":
                print(f"\n✅ Información encontrada en: {url}\n")
                print(f"📄 Respuesta: {respuesta.strip()}")
                guardar_respuesta(url, args.query, respuesta.strip())
                break
            else:
                print(f"❌ Información no encontrada en: {url}")
