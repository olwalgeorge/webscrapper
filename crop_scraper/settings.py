# Scrapy settings for crop_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'crop_scraper'

SPIDER_MODULES = ['crop_scraper.spiders']
NEWSPIDER_MODULE = 'crop_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # Temporarily disabled to avoid recursion issue

# Configure delays for requests (be respectful)
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY_SPREAD = 0.5

# Enable autothrottling to automatically adjust delays
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Configure a user agent
USER_AGENT = 'crop_scraper (+http://www.yourdomain.com)'

# Configure pipelines
ITEM_PIPELINES = {
    'crop_scraper.pipelines.ValidationPipeline': 300,
    'crop_scraper.pipelines.DatabasePipeline': 400,
    'crop_scraper.pipelines.JsonWriterPipeline': 500,
}

# Configure item exporters
FEED_EXPORT_ENCODING = 'utf-8'

# Database settings
DATABASE_URL = 'sqlite:///crops.db'

# Enable rotating proxies and user agents for anti-bot protection
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'crop_scraper.middlewares.RotateUserAgentMiddleware': 400,
    # 'crop_scraper.middlewares.ProxyMiddleware': 350,  # Disabled for testing
    # 'crop_scraper.middlewares.DelayMiddleware': 300,  # Disabled - using DOWNLOAD_DELAY instead
    # 'crop_scraper.middlewares.ScrapyApiMiddleware': 200,  # Disabled for testing
}

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'scraping.log'

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Set settings whose default value is deprecated
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

# ScrapyAPI settings (when using ScrapyAPI service)
SCRAPYAPI_KEY = os.getenv('SCRAPYAPI_KEY', 'your-scrapyapi-key-here')
SCRAPYAPI_ENABLED = False  # Set to True when using ScrapyAPI

# Additional anti-bot settings
COOKIES_ENABLED = True
TELNETCONSOLE_ENABLED = False

# Cache settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'
