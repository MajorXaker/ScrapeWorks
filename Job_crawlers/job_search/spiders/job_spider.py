import re

import scrapy


class JobSpider(scrapy.Spider):
    name = 'JobSpider'

    # TODO a json file with allowed domains and start urls
    allowed_domains = ['spb.hh.ru', ]
    start_urls = [
        'https://spb.hh.ru/search/vacancy?search_field=name&search_field=company_name&search_field=description&text=Python+backend&clusters=true&ored_clusters=true&enable_snippets=true&from=suggest_post',
    ]

    id = -1

    def parse_details(self, response):
        self.id = self.id + 1
        # description group
        description = response.xpath('.//div[@data-qa="vacancy-description"]')
        description_texts = []
        for tag in description.xpath('.//*[name()="p" or name()="ul"]'):
            if tag.xpath('name()').get() == 'p':
                text_pieces = tag.xpath('descendant-or-self::text()').getall()
                combined_phrase = ''.join(text_pieces)
                description_texts.append(combined_phrase)
            else:
                # if not p then it's ul tag
                list = tag.xpath('.//li/descendant-or-self::text()').getall()
                description_texts.append(list)

        yield {
            'id': self.id,
            'position_title': ''.join(response.xpath('//h1[@class="bloko-header-1"]/text()').getall()),
            'salary_text': response.xpath('//div[@data-qa="vacancy-salary"]/span/text()').getall(),
            'employer': ''.join(response.xpath('//a[@class="vacancy-company-name"]/span/text()').getall()),
            'description': description_texts,
            'url': response.url
        }

    def parse(self, response):
        vacancies = response.xpath('//div[@class="vacancy-serp-item"]')
        vacancies_details_urls = []
        for vacancy_block in vacancies:
            vacancy_url = vacancy_block.xpath(
                './/h3[@class="bloko-header-section-3"]//a[@class="bloko-link"]/@href').get()
            vacancies_details_urls.append(vacancy_url)
        for vacancy_detail_url in vacancies_details_urls:
            yield scrapy.Request(vacancy_detail_url, self.parse_details)



