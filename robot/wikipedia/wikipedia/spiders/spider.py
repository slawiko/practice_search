from bs4 import BeautifulSoup
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider

from wikipedia.items import WikipediaItem


postfixes = [
    'Main_Page',
    'Free_Content',
    'Talk:',
    'File:',
    'Help:',
    'Draft:',
    'Portal:',
    'Special:',
    'Template:',
    'Category:',
    'Wikipedia:',
    'Template_talk:'
]


class PagesSpider(CrawlSpider):
    """
    the Page Spider for wikipedia
    """

    name = "wikipedia_pages"
    allowed_domains = ["wikipedia.org"]
    visited_cnt = 0

    start_urls = [
        "https://en.wikipedia.org/wiki/Metallica",
        "https://en.wikipedia.org/wiki/S.T.A.L.K.E.R.",
        "https://en.wikipedia.org/wiki/Antirrhinum",
        "https://en.wikipedia.org/wiki/Apple_Inc.",
        "https://en.wikipedia.org/wiki/Alexander_Lukashenko"
    ]

    rules = (
        Rule(
            LinkExtractor(
                allow="https://en\.wikipedia\.org/wiki/.+",
                deny=map(lambda s: 'https://en\.wikipedia\.org/wiki/%s.*' % s, postfixes),
                restrict_xpaths='(//div[@id="mw-content-text"]//a)[position() < 101]'
            ),
            follow=True,
            callback='parse_wikipedia_page'
        ),
    )

    def parse_wikipedia_page(self, response):
        if self.visited_cnt > 10000:
            raise CloseSpider('That\'s enough')
        print self.visited_cnt

        item = WikipediaItem()
        item['title'] = response.xpath('//*[@id="firstHeading"]/text()').extract()[0]
        item['url'] = response.url
        item['snippet'] = BeautifulSoup(response.xpath('//div[@id="mw-content-text"]/div/p[1]').extract_first(), "lxml").text[:255]+"..."

        must = ' or '.join(['starts-with(@href, "/wiki/")', 'contains(@href, "https://en\.wikipedia\.org/wiki/")'])
        must_not = ' or '.join(map(lambda s: "contains(@href, '%s')" % s, postfixes))
        xpath = '(((//div[@id="mw-content-text"]//a)[{}][not({})])/@href)[position() < 101]'.format(must, must_not)
        item['urls'] = response.xpath(xpath).extract()

        self.visited_cnt += 1

        return item
