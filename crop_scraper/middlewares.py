# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
import random
import time


class RotateUserAgentMiddleware(UserAgentMiddleware):
    """Middleware to rotate user agents for better anti-bot protection"""
    
    def __init__(self, user_agent=''):
        self.user_agent = user_agent
        self.user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = ua


class ProxyMiddleware:
    """Middleware to rotate proxies (implement if using proxy services)"""
    
    def __init__(self):
        # Add your proxy list here
        self.proxies = [
            # 'http://proxy1:port',
            # 'http://proxy2:port',
        ]
    
    def process_request(self, request, spider):
        if self.proxies:
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy


class DelayMiddleware:
    """Middleware to add random delays between requests"""
    
    def __init__(self):
        self.delay_range = (1, 3)  # Random delay between 1-3 seconds
    
    def process_request(self, request, spider):
        # Use download_delay setting instead of blocking sleep
        delay = random.uniform(*self.delay_range)
        request.meta['download_delay'] = delay


class ScrapyApiMiddleware:
    """Middleware for ScrapyAPI integration"""
    
    def __init__(self, api_key, enabled=False):
        self.api_key = api_key
        self.enabled = enabled
        self.api_url = 'http://api.scraperapi.com'
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            api_key=crawler.settings.get('SCRAPYAPI_KEY'),
            enabled=crawler.settings.get('SCRAPYAPI_ENABLED', False)
        )
    
    def process_request(self, request, spider):
        if self.enabled and self.api_key:
            # Route request through ScrapyAPI
            api_url = f"{self.api_url}?api_key={self.api_key}&url={request.url}"
            request = request.replace(url=api_url)
        return request


class CropScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn't have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
