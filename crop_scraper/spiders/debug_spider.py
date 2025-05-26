import scrapy


class DebugSpider(scrapy.Spider):
    name = 'debug'
    start_urls = ['http://httpbin.org/get']
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 0,
    }
    
    def parse(self, response):
        self.logger.info(f"SUCCESS: Got response from {response.url}")
        self.logger.info(f"Status: {response.status}")
        self.logger.info(f"Content length: {len(response.body)}")
        
        # Just yield a simple dict instead of using items
        yield {
            'url': response.url,
            'status': response.status,
            'content_length': len(response.body)
        }
