import scrapy
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://oas.fon.bg.ac.rs']  # Start URL of the website you want to crawl
    visited_urls = set()  # Set to keep track of visited URLs

    def parse(self, response):
        # Extract text content from specific HTML elements
        title = response.css('title::text').get()
        url = response.url
        html = response.body.decode(response.encoding)

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Extract text from elements within <main> tags
        main_content = soup.find('main')
        if main_content:
            text_content = ''
            for tag in main_content.find_all(['p', 'table', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tg', 'tn', 'th', 'ul', 'li','a','ol']):
                text_content += tag.get_text(separator=' ', strip=True) + '\n'

            yield {
                'title': title,
                'url': url,
                'text_content': text_content
            }

        # Mark the current URL as visited
        self.visited_urls.add(url)

        # Follow links if depth is less than 2 and within the same domain
        if response.meta.get('depth', 0) < 2:
            for link in response.css('a::attr(href)').getall():
                if self.should_follow_link(link):
                    yield response.follow(link, callback=self.parse)

    def should_follow_link(self, link):
        # Exclude certain links based on patterns
        exclude_patterns = [
            '/vesti/',
            '/Category/',
            '/vazno-obavestenje/',
            '/ispiti/',
            '/kolokvijumi/',
            '/predavanja-seminari-radionice/',
            '/strucna-praksa/',
            '/medjunarodna-saradnja/',
            '/upis/',
            '/krediti-i-stipendije/',
            '/konsultacije/',
            '/zavrsni-radovi/',
            '/raspored-ispita/',
            '/????/'
        ]

        # Add your logic here to determine whether to follow a link or not
        parsed_link = urlparse(link)
        if (parsed_link.netloc == 'oas.fon.bg.ac.rs' and
            not any(pattern in link for pattern in exclude_patterns) and
            not re.search(r'\d', link) and
            link not in self.visited_urls):  # Check if the link is not in visited URLs
            return True
        return False
