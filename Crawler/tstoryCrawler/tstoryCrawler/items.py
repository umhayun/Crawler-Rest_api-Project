# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TstorycrawlerItem(scrapy.Item):
    media=scrapy.Field()
    date = scrapy.Field()
    keywords = scrapy.Field()
    url = scrapy.Field()
    blog_id = scrapy.Field()
    entry_id = scrapy.Field()
    title = scrapy.Field()
    writer = scrapy.Field()
    content = scrapy.Field()
    comment = scrapy.Field()
    like = scrapy.Field()
    job_id = scrapy.Field()
    pass
