# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector
from urllib.parse import urlparse

def normalizar_url(raw_url):
    parsed = urlparse(raw_url)
    netloc = parsed.netloc.replace("www.", "")
    path = parsed.path.rstrip("/")
    return f"{netloc}{path}"



class ScrapingKmlPipeline:
    def process_item(self, item, spider):
        return item
class GuardarHTMLenMySQL:
    def open_spider(self, spider):
        self.conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="1573",
            database="enriquecimiento_datos_negocio"
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        url_normalizada = normalizar_url(item["url"])
        print(f"🔗 Guardando HTML de {url_normalizada} en la base de datos.")
        self.cursor.execute(
            "REPLACE INTO html (url, html) VALUES (%s, %s)",
            (url_normalizada, item["html"])
        )
        self.conn.commit()
        return item

