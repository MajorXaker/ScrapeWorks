# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re

from .items import JobSearchItem


class JobSearchPipeline:
    #     def process_item(self, item, spider):
    #         return item

    def blank_lines_cleanup(self, iterable: list) -> list:
        element = 0
        while element < len(iterable):
            item = iterable[element]
            if item == '' or len(item) == 0:
                iterable.pop(element)
            else:
                if isinstance(item, list):
                    self.blank_lines_cleanup(item)
                element += 1
        return iterable

    @staticmethod
    def rm_non_break_spc(line: str, at_all=False) -> str:
        if at_all:
            return re.sub(r'\s+', '', line)
        else:
            return re.sub(r'\s+', ' ', line)

    @staticmethod
    def unspace(string: str) -> str:
        return string.replace(' ', '')

    @staticmethod
    def define_currency(salary_strings: list) -> str or None:
        """Defines what currency is given, returns its codename, returns None if currency is not found"""

        currencies = {
            'EUR': ['eur', 'евро'],
            'USD': ['usd', 'долларов'],
            'RUB': ['rub', 'рублей', 'руб.'],
        }
        for currency_code, currency_alt_names in currencies.items():
            for salary_item in salary_strings:
                if salary_item in currency_alt_names:
                    return currency_code, salary_item
        return None, None

    def break_up_salary(self, strings: list) -> dict:
        strings = [itm.lower() for itm in strings]
        salary = {}
        try:
            min_salary_raw = strings[strings.index('от') + 1]
        except ValueError:
            salary['min_salary'] = None
        else:
            min_salary = self.unspace(min_salary_raw)
            salary['min_salary'] = int(min_salary)
            strings.pop(strings.index(min_salary_raw))
            strings.pop(strings.index('от'))

        try:
            min_salary_raw = strings[strings.index('до') + 1]
        except ValueError:
            salary['max_salary'] = None
        else:
            min_salary = self.unspace(min_salary_raw)
            salary['max_salary'] = int(min_salary)
            strings.pop(strings.index(min_salary_raw))
            strings.pop(strings.index('до'))

        salary['currency'], orig_curr_name = self.define_currency(strings)
        if salary['currency'] is not None:
            strings.pop(strings.index(orig_curr_name))

        salary['other_details'] = strings

        return salary

    def process_item(self, item, spider):
        vacancy = JobSearchItem()
        # id processing
        vacancy['id'] = item['id']
        # title processing
        vacancy['job_title'] = item['position_title']
        # salary processing
        salary_prepared = []
        for string in item['salary_text']:
            item_no_non_break_space = self.rm_non_break_spc(string, at_all=False)
            item_unspaced = item_no_non_break_space.strip(' ')
            salary_prepared.append(item_unspaced)

        salary_no_blanks = self.blank_lines_cleanup(salary_prepared)

        vacancy['salary'] = self.break_up_salary(salary_no_blanks)

        # employer processing
        vacancy['employer'] = self.rm_non_break_spc(item['employer'])
        # description processing
        description = self.blank_lines_cleanup(item['description'])
        vacancy['description'] = description
        vacancy['url'] = item['url']

        return vacancy
