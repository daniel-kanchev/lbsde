import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from lbsde.items import Article
import requests
import json

class LbsdeSpider(scrapy.Spider):
    name = 'lbsde'
    start_urls = ['https://www.lbs.de/search/press.jsp?pressRegion=0&category=Guthmann-Blog']

    def parse(self, response):
        json_res = json.loads(requests.get("https://www.lbs.de/search/press.jsp?"
                                           "pressRegion=0&category=Guthmann-Blog").text)

        docs = json_res['response']['docs']
        for article in docs:
            link = article['link']
            date = article['date']
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="post_text_inner"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
