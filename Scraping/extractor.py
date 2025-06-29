from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraping_kml.spiders.kml_spider import KmlSpider
import mysql.connector
from urllib.parse import urlparse

def normalizar_url(raw_url):
    parsed = urlparse(raw_url)
    netloc = parsed.netloc.replace("www.", "")
    path = parsed.path.rstrip("/")
    return f"{netloc}{path}"

def url_ya_guardada(url, conexion):
    url_normalizada = normalizar_url(url)
    cursor = conexion.cursor()
    cursor.execute("SELECT 1 FROM html WHERE url = %s LIMIT 1", (url_normalizada,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado is not None


def guardar_html(url, html, conexion):
    url_normalizada = normalizar_url(url)
    print(f"🔗 Guardando HTML de {url_normalizada} en la base de datos.")
    cursor = conexion.cursor()
    cursor.execute("REPLACE INTO html (url, html) VALUES (%s, %s)", (url_normalizada, html))
    conexion.commit()
    cursor.close()


def run_scraper(urls, query, db_path, deep):
    # Conexión a la base de datos local
    conexion = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="1573",
        database="enriquecimiento_datos_negocio"
    )
    print("🔗 Conexión a la base de datos establecida.")
    print(urls)
    # Filtrar URLs que ya están en la base de datos
    for url in urls:
        if url_ya_guardada(url, conexion):
            print(normalizar_url(url))
            print(f"🔗 URL ya guardada: {url}")
        else:
            print(normalizar_url(url))
            print(f"🔗 URL nueva para scrapear: {url}")
    urls_filtradas = [url for url in urls if not url_ya_guardada(url, conexion)]
    print(f"🔍 Se van a scrapear {len(urls_filtradas)} URLs (filtradas de {len(urls)} totales).")

    if not urls_filtradas:
        print("✅ No hay nuevas URLs por scrapear.")
        return

    # Definir configuración y lanzar el proceso Scrapy
    settings = get_project_settings()
    settings.set('ITEM_PIPELINES', {
        'scraping_kml.pipelines.GuardarHTMLenMySQL': 1,
    })

    # Puedes pasar conexión u otros valores a través del `KmlSpider` si lo necesitas
    process = CrawlerProcess(settings)
    process.crawl(KmlSpider, start_urls=urls_filtradas, query=query, depth=deep)
    process.start()

    conexion.close()
