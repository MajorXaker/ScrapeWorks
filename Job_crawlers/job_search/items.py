# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobSearchItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    job_title = scrapy.Field()
    salary = scrapy.Field()
    employer = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()

