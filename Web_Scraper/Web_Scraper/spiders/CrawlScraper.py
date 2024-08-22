from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from w3lib.html import remove_tags
from parsel import Selector
import os
import re
import csv
from math import ceil

class CrawlscraperSpider(CrawlSpider):
    name = "CrawlScraper"
    allowed_domains = ["indiabix.com"]
    start_urls = ["https://www.indiabix.com/"]

    rules = (
        Rule(LinkExtractor(allow=['aptitude', 'verbal-reasoning', 'verbal-ability', 'logical-reasoning', 'c-programming', 'c-sharp-programming', 'java-programming', 'cpp-programming'], deny=['discussion']), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(CrawlscraperSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()
        self.output_folder = "Extracted Files"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def parse_item(self, response):
        if response.url in self.visited_urls:
            return

        self.visited_urls.add(response.url)

        print(f"URL: {response.url}")

        html_content = response.text
        selector = Selector(text=html_content)

        replacements = {
            'span.mdi.mdi-alpha-a-circle-outline': '<p>A</p>',
            'span.mdi.mdi-alpha-b-circle-outline': '<p>B</p>',
            'span.mdi.mdi-alpha-c-circle-outline': '<p>C</p>',
            'span.mdi.mdi-alpha-d-circle-outline': '<p>D</p>'
        }

        for css_selector, replacement in replacements.items():
            for span in selector.css(css_selector):
                html_content = html_content.replace(span.get(), replacement)
            
            for span in selector.css(f'{css_selector}[id]'):
                html_content = html_content.replace(span.get(), replacement)

        modified_selector = Selector(text=html_content)

        direction_html = modified_selector.css('div#direction').extract_first(default='')
        content_html_list = modified_selector.css('div.bix-div-container').extract()

        div_per_page = 6
        total_pages = ceil(len(content_html_list) / div_per_page)

        for page_num in range(total_pages):
            start = page_num * div_per_page
            end = start + div_per_page
            page_content_html = content_html_list[start:end]

            combined_content_html = direction_html + ''.join(page_content_html)
            content_text = remove_tags(combined_content_html).strip()

            content_text = re.sub(r'\n\s*\n+', '\n\n', content_text)
            
            self.save_content(response.url, page_num + 1, content_text)

    def save_content(self, url, page_num, content):
        base_filename = url.replace("https://www.indiabix.com/", "").replace("/", "_")
        filename = os.path.join(self.output_folder, f"{base_filename}_page_{page_num}.txt")

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
            print(f"Content written to {filename}")



class CareerRideScraperSpider(CrawlSpider):
    name = "CareerRideScraper"
    allowed_domains = ["careerride.com"]
    start_urls = ["https://www.careerride.com/online-aptitude-test.aspx"]

    custom_settings = {
        'DEPTH_LIMIT': 1  
    }

    rules = (
        Rule(LinkExtractor(allow=[], deny=['post']), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(CareerRideScraperSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()
        self.output_folder = "Extracted Files"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def parse_item(self, response):
        if response.url in self.visited_urls:
            return

        self.visited_urls.add(response.url)

        print(f"URL: {response.url}")

        html_content = response.text
        selector = Selector(text=html_content)

        tables_html_list = selector.css('table.paratitle1').extract()

        combined_tables_html = ''.join(tables_html_list)
        content_text = remove_tags(combined_tables_html).strip()

        content_text = re.sub(r'\n\s*\n+', '\n\n', content_text)
        
        self.save_content(response.url, content_text)

    def save_content(self, url, content):
        base_filename = url.replace("https://www.careerride.com/", "").replace("/", "_")
        filename = os.path.join(self.output_folder, f"{base_filename}.txt")

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
            print(f"Content written to {filename}")


class PrepInstaScraperSpider(CrawlSpider):
    name = "PrepInsta"
    allowed_domains = ["prepinsta.com"]
    start_urls = ["https://prepinsta.com/complete-aptitude-preparation/"]

    custom_settings = {
        'DEPTH_LIMIT': 1
    }

    rules = (
        Rule(LinkExtractor(allow=['questions', 'question-answer'], deny=[]), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(PrepInstaScraperSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()
        self.output_folder = "Extracted Files"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def parse_item(self, response):
        if response.url in self.visited_urls:
            return

        self.visited_urls.add(response.url)

        print(f"URL: {response.url}")

        html_content = response.text
        selector = Selector(text=html_content)

        # Extract content from divs with specific classes
        dash_question_divs = selector.css('div.dash-question').extract()
        dash_ans_title_divs = selector.css('div.dash-ls-ans-title.dash-displaynone').extract()
        dash_explanation_divs = selector.css('div.dash-explanation.collapse.show').extract()

        # Combine all extracted HTML content
        combined_html = ''.join(dash_question_divs + dash_ans_title_divs + dash_explanation_divs)
        content_text = self.remove_tags(combined_html).strip()

        content_text = re.sub(r'\n\s*\n+', '\n\n', content_text)
        
        self.save_content(response.url, content_text)

    def remove_tags(self, html_content):
        # Remove HTML tags, can use other methods if needed
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html_content)

    def save_content(self, url, content):
        base_filename = url.replace("https://prepinsta.com/", "").replace("/", "_")
        filename = os.path.join(self.output_folder, f"{base_filename}.txt")

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
            print(f"Content written to {filename}")


class CrawlscraperSpider(CrawlSpider):
    name = "indiabix"
    allowed_domains = ["indiabix.com"]
    start_urls = ["https://www.indiabix.com/"]

    rules = (
        Rule(LinkExtractor(allow=['aptitude', 'verbal-reasoning', 'verbal-ability', 'logical-reasoning'], deny=['discussion']), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(CrawlscraperSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()
        self.output_folder = "Extracted Files"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        self.csv_file = open(os.path.join(self.output_folder, 'questions.csv'), 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Question', 'Option 1', 'Option 2', 'Option 3', 'Option 4', 'Answer'])

    def parse_item(self, response):
        if response.url in self.visited_urls:
            return

        self.visited_urls.add(response.url)

        print(f"URL: {response.url}")

        # Directly use the response as it is already a Selector object
        questions = response.css('.bix-div-container')

        for question in questions:
            question_text = question.css('.bix-td-qtxt.table-responsive.w-100').get()
            question_text = remove_tags(question_text).strip() if question_text else None

            # Extracting options from each row in the options table
            options = question.css('.bix-tbl-options tr td:last-child')  # Assuming options are in the last column of each row
            options_text = [remove_tags(opt.get()).strip() for opt in options if opt.get()]

            answer_span = question.css('.bix-ans-option span::attr(class)').get()
            answer_map = {
                'mdi mdi-alpha-a-circle-outline': 1,
                'mdi mdi-alpha-b-circle-outline': 2,
                'mdi mdi-alpha-c-circle-outline': 3,
                'mdi mdi-alpha-d-circle-outline': 4
            }
            answer_index = answer_map.get(answer_span, None)

            print("Question:", question_text)
            print("Options:", options_text)

            self.csv_writer.writerow([
                question_text,
                options_text[0],
                options_text[1],
                options_text[2],
                options_text[3],
                options_text[answer_index - 1]
            ])

