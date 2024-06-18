# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BlogCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    media=scrapy.Field()
    date = scrapy.Field()
    keywords = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    writer = scrapy.Field()
    content = scrapy.Field()
    comment = scrapy.Field()
    like = scrapy.Field()
    job_id = scrapy.Field()
    pass

