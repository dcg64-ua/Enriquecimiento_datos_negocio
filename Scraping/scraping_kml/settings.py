BOT_NAME = "scraping_kml"

SPIDER_MODULES = ["scraping_kml.spiders"]
NEWSPIDER_MODULE = "scraping_kml.spiders"

ROBOTSTXT_OBEY = True
FEED_EXPORT_ENCODING = "utf-8"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
LOG_LEVEL = 'INFO'
LOG_SHORT_NAMES = True
