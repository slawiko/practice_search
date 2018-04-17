from scrapy.spiders import CrawlSpider

from contest.items import ContestItem


class PagesSpider(CrawlSpider):
    name = "wikipedia_pages"
    domain = "ru.wikipedia.org"
    allowed_domains = [domain]
    visited_cnt = 0

    urlid = open("../KR/urlid.csv", "r")

    csv_file = urlid.readlines()

    urls = {}
    inv_urls = {}

    for row in csv_file:
        pair = row.split(",", 1)
        id, url = pair[0], pair[1][:-1]
        urls[id] = "https://" + domain + url
        inv_urls[url] = id

    start_urls = urls.values()

    def parse(self, response):
        item = ContestItem()
        item['title'] = response.xpath('//*[@id="firstHeading"]/text()').extract()[0]
        item['url'] = response.url.split(self.domain)[1]
        item['id'] = self.inv_urls[item['url']]

        xpath = '//div[@id="mw-content-text"]//a/@href'
        page_urls = response.xpath(xpath).extract()

        same_urls = []
        for url in page_urls:
            url = url.encode('utf-8')
            if url in self.inv_urls:
                same_urls.append(url)

        print self.visited_cnt, "same", len(same_urls), "page_urls", len(page_urls)
        item['urls'] = same_urls

        self.visited_cnt += 1
        return item
