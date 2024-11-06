# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


import scrapy

class NorthDakotaBusinessDataCrawlingItem(scrapy.Item):
    company_name = scrapy.Field()
    company_id = scrapy.Field()
    filing_type = scrapy.Field()
    status = scrapy.Field()
    standing_ar = scrapy.Field()
    standing_ra = scrapy.Field()
    standing_other = scrapy.Field()
    formed_in = scrapy.Field()
    term_of_duration = scrapy.Field()
    initial_filing_date = scrapy.Field()
    principal_address = scrapy.Field()
    mailing_address = scrapy.Field()
    ar_due_date = scrapy.Field()
    registered_agent = scrapy.Field()
    commercial_registered_agent = scrapy.Field()
    owner_name = scrapy.Field()

