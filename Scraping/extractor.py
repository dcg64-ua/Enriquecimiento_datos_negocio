from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraping_kml.spiders.kml_spider import KmlSpider

def run_scraper(urls, query, db_path, deep):
    settings = get_project_settings()
    settings.set('FEEDS', {
        db_path: {
            'format': 'json',
            'encoding': 'utf8',
            'overwrite': True
        }
    })
    process = CrawlerProcess(settings)
    process.crawl(KmlSpider, start_urls=urls, query=query, depth=deep)
    process.start()
