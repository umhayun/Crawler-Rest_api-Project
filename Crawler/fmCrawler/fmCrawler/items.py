# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FmcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    media=scrapy.Field()
    date = scrapy.Field()
    keywords = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    writer = scrapy.Field()
    content = scrapy.Field()
    comment = scrapy.Field()
    like = scrapy.Field()

    views = scrapy.Field()
    post_id = scrapy.Field()
    pass
