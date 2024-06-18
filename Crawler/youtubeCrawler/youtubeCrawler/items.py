# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YoutubeCrawlerItem(scrapy.Item):
    #define the fields for your item here like:
    #name = scrapy.Field()
    #pass
    media = scrapy.Field() 
    keyword = scrapy.Field()
    post_id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    views = scrapy.Field()
    date = scrapy.Field()
    writer = scrapy.Field()
    like = scrapy.Field()
    comment_count = scrapy.Field()
    comment = scrapy.Field() # {user_name, comment_day, comment_date, comment, like_count, hate_count}
    job_id = scrapy.Field()
    # crawled_date = scrapy.Field()