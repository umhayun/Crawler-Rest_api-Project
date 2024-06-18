# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CafecrawlerItem(scrapy.Item):
  media=scrapy.Field()
  date = scrapy.Field()
  keywords = scrapy.Field()
  real_url = scrapy.Field()
  url = scrapy.Field()
  title = scrapy.Field()
  writer = scrapy.Field()
  content = scrapy.Field()
  comment = scrapy.Field()
  views = scrapy.Field()
  like = scrapy.Field()
  job_id = scrapy.Field()
  pass