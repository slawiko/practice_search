# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ContestItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    urls = scrapy.Field()
    title = scrapy.Field()
