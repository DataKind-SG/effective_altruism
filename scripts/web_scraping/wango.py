import coloredlogs, logging
import csv

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser

CATEGORY_REQUEST_URL = 'http://www.wango.org/resources.aspx?section=ngodir&sub=list&newsearch=1&regionID=35&col=cc3300'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
coloredlogs.install()

csvwriter = csv.writer( open('wango.csv', 'w') )
csvwriter.writerow(['name', 'cause_area', 'country', 'city'])

categories = []
category = ''
curr_page = 1

def make_formdata(category, page=None): 
    formdata = {
        'Countries': '96,104,116,360,418,458,608,626,702,704,764,0',
        'InterestAreas': category
    }

    if page:
        formdata['currpage'] = str(page)

    return formdata

def get_country_city(raw):
    entries = raw.split(',')

    if len(entries) <= 1:
        return ''.join(entries), ''

    country = entries.pop()
    city = ', '.join(entries)

    return country, city


class WangoSpider(scrapy.Spider):
    name = 'wango'
    # allowed_domains = ['http://www.wango.org/']
    start_urls = ['https://www.google.com/']

    def parse(self, response):
        yield FormRequest(
            url=CATEGORY_REQUEST_URL,
            formdata=make_formdata('ALL'),
            callback=self.extract_categories
        )

    def extract_categories(self, response):
        global categories

        raw_categories = response.css('#InterestAreas option::text')[2:]
        categories = [category.extract() for category in raw_categories]

        yield Request(
            'https://www.google.com',
            callback=self.visit_next_category,
            dont_filter=True
        )

    def visit_next_category(self, response=None):
        global category, curr_page

        logger.info(categories)

        if not categories:
            return

        category = categories.pop()
        logger.info( 'Visiting {}'.format(category) )

        yield FormRequest(
            url=CATEGORY_REQUEST_URL,
            formdata=make_formdata(category),
            callback=self.parse_category
        )
    
    def parse_category(self, response):
        global curr_page

        raw_names = response.css('a b::text')[:-2]
        names = [name.extract() for name in raw_names]

        raw_country_citys = response.css('td .contentmargin0::text')
        country_citys = [get_country_city(raw.extract()) for raw in raw_country_citys]

        for name, cc in zip(names, country_citys):
            csvwriter.writerow([name, category, cc[0], cc[1]])

        logger.debug( '{} names, {} country/citys'.format(len(names), len(country_citys)) )
 
        # check if next button is present
        possible_nexts_raw = response.css('div[align="left"] a::text')

        if len(possible_nexts_raw) > 1:
            is_next_valid = possible_nexts_raw[-2].extract() == '>'

        else:
            is_next_valid = False


        if is_next_valid:
            curr_page += 1

            yield FormRequest(
                url=CATEGORY_REQUEST_URL,
                formdata=make_formdata(category, curr_page),
                callback=self.parse_category,
                dont_filter=True
            )

        else:
            curr_page = 1
            yield Request(
                'https://www.google.com',
                callback=self.visit_next_category,
                dont_filter=True
            )



process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(WangoSpider)
process.start()
