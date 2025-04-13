import scrapy
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re


class KmlSpider(scrapy.Spider):
    name = "kml_spider"

    def __init__(self, start_urls=None, **kwargs):
        self.start_urls = start_urls or []
        self.visited = set()
        super().__init__(**kwargs)

    def parse(self, response):
        url = response.url

        # Solo seguir si es HTML
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        if 'text/html' not in content_type:
            return  # No seguimos si no es HTML

        if url in self.visited:
            return
        self.visited.add(url)

        # Limpieza de HTML con BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Eliminar etiquetas irrelevantes
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'link', 'meta']):
            tag.decompose()

        # Eliminar comentarios HTML
        for comment in soup.find_all(string=lambda text: isinstance(text, (type(soup.comment)))):
            comment.extract()

        # Extraer texto y limpiar
        raw_text = soup.get_text(separator=" ").strip()

        # Reemplazar múltiples espacios y saltos de línea por uno solo
        clean_text = re.sub(r"\s+", " ", raw_text)


        yield {
            "url": url,
            "html": clean_text,
            "profundidad": self.get_depth_from_url(url)
        }

        # Seguir enlaces internos (solo si es HTML)
        for link in response.css("a::attr(href)").getall():
            full_url = urljoin(response.url, link)
            if urlparse(full_url).netloc == urlparse(response.url).netloc:
                yield response.follow(full_url, callback=self.parse)

    def get_depth_from_url(self, url):
        path = urlparse(url).path.strip("/")
        if not path:
            return 1
        return len(path.split("/")) + 1
