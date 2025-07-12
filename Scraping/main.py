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
import mysql.connector
from extractor import normalizar_url



def database_connection():
    conexion = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="user",
    password="1573",
    database="enriquecimiento_datos_negocio")

    cursor = conexion.cursor(dictionary=True)
    return conexion, cursor


def dividir_en_bloques(lista, tam_bloque):
    return [lista[i:i + tam_bloque] for i in range(0, len(lista), tam_bloque)]

def agrupar_por_raiz(data):
    grupos = defaultdict(list)
    for entrada in data:
        url = entrada["url"]
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url  # suposición básica
        dominio = urlparse(url).netloc
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
    

    
    urls_normalizadas = [normalizar_url(url) for url in urls]
    print("🔗 URLs normalizadas:", urls_normalizadas)

    conexion, cursor = database_connection()

    # Creamos la consulta para cada URL con un LIKE para que tome todas las URLs que empiecen con la URL normalizada
    placeholders = ','.join([f"%s" for _ in urls_normalizadas])
    print(f"🔗 Consultando la base de datos para URLs normalizadas con LIKE: {placeholders}")

    # Preparamos la consulta con LIKE usando % al final
    print("La profundidad máxima es:", args.deep)
    consulta = (
    "SELECT url, html, profundidad FROM html WHERE " +
    " OR ".join([f"(url LIKE %s AND profundidad <= {args.deep})" for _ in urls_normalizadas]))


    # Creamos las URLs normalizadas con el comodín '%' al final
    urls_with_wildcard = [url + "%" for url in urls_normalizadas]

    # Ejecutamos la consulta con las URLs normalizadas con el % al final
    cursor.execute(consulta, urls_with_wildcard)
    data = cursor.fetchall()
    print(f"🔗 Se encontraron {len(data)} entradas en la base de datos para las URLs normalizadas.")



    # Guardar el contenido extraído de la base de datos en un archivo JSON
    with open("datos_desde_db.json", "w", encoding="utf-8") as f:
        # Vaciar el archivo antes de escribir el nuevo contenido
        f.truncate(0)
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Archivo 'datos_desde_db.json' generado con {len(data)} entradas.")


    cursor.close()
    conexion.close()
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
