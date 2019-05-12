import scrapy
import logging
import time
import string

from scrapy.loader import ItemLoader
from fbcrawl.spiders.fbcrawl import FacebookSpider
from fbcrawl.items import MembersItem

class MembersSpider(FacebookSpider):
    """
    parse post reactions, given a post(needs credentials)
    """
    name = "members"
    custom_settings = {
        'FEED_EXPORT_FIELDS': ['profile'],
        'DUPEFILTER_CLASS' : 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS':1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def parse_page(self, response):
        members = response.xpath("//a[contains(@href,'view=members')]/@href")
        members = response.urljoin(members[0].extract())
        yield scrapy.Request(members, callback=self.parse_membersPage)

    def parse_membersPage(self, response):
        for members in response.xpath("//a[contains(@href,'nonfriend')]"):
            members = response.xpath("//a[contains(@href,'nonfriend')]/@href")
            members = response.urljoin(members[0].extract())
            yield scrapy.Request(members, callback=self.parse_members)
        
    def parse_members(self,response):
        for i,reply in enumerate(response.xpath(".//table[contains(@id, 'member_')]//@id")):
            rpl = reply.extract()
            self.logger.info('{} member @ page '.format(rpl))
            new = ItemLoader(item=MembersItem(),selector=reply)
            new.context['lang'] = self.lang
            new.add_value('profile',reply.extract().replace('member_','https://m.facebook.com/profile.php?id='))       
            yield new.load_item()
        new_page = response.xpath("//div/div/a/@href").extract()
        time.sleep(1)
        self.logger.info('finding new page ')
        if not new_page :
            self.logger.info('no more members to fetch')
        else :
            self.logger.info('new page found')
            new_page = response.urljoin(new_page[0])
            yield scrapy.Request(new_page, callback=self.parse_members)



