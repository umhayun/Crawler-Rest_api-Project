# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
# Scrapy settings for youtubeCrawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

load_dotenv()

BOT_NAME = 'youtubeCrawler'

SPIDER_MODULES = ['youtubeCrawler.spiders']
NEWSPIDER_MODULE = 'youtubeCrawler.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'youtubeCrawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'youtubeCrawler.middlewares.YoutubeCrawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'youtubeCrawler.middlewares.YoutubeCrawlerDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'youtubeCrawler.pipelines.YoutubeCrawlerPipeline': 300,
#}

ITEM_PIPELINES = {
    'youtubeCrawler.pipelines.YoutubeCrawlerPipeline': 300,
}

OBOTSTXT_OBEY = True

FEED_EXPORT_ENCODING='utf-8'

CONCURRENT_REQUESTS = 1
DOWNLOAD_TIMEOUT = 10
RETRY_TIME = 2
DOWNLOAD_DELAY = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 1


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

FEED_EXPORT_ENCODING='utf-8'

LOG_LEVEL = "ERROR"
LOG_FORMAT = '%(levelname)s: %(message)s'
# LOG_STDOUT = True



ELASTICSEARCH_SERVER = os.environ.get('ELASTICSEARCH_SERVER')
ELASTICSEARCH_PORT = int(os.environ.get('ELASTICSEARCH_PORT'))
MARIADB_HOST = os.environ.get('MARIADB_HOST')
MARIADB_PORT = int(os.environ.get('MARIADB_PORT'))
MARIADB_USERNM = os.environ.get('MARIADB_USERNM')
MARIADB_PASSWD = os.environ.get('MARIADB_PASSWD')
MARIADB_DBNM = os.environ.get('MARIADB_DBNM')
LOG_PATH = f'{os.environ.get("LOG_PATH")}youtube/'
