import scrapy
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://youtube.com']  # Start URL of the website you want to crawl
    visited_urls = set() 

    def parse(self, response):
    
        title = response.css('title::text').get()
        url = response.url
        html = response.body.decode(response.encoding)

        
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

        
        self.visited_urls.add(url)

        
        if response.meta.get('depth', 0) < 2:
            for link in response.css('a::attr(href)').getall():
                if self.should_follow_link(link):
                    yield response.follow(link, callback=self.parse)

    def should_follow_link(self, link):
        # Exclude certain links based on patterns
        exclude_patterns = [
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
