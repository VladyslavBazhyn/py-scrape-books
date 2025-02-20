from pathlib import Path

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for product in response.css(".product_pod"):
            yield {
                "title": product.css("h3").css("a::attr(title)").get(),
                "price": float(product.css(".price_color::text").get()[1:]),
                # "amount_in_stock": product.css("instock"), - need to get detail page
                # "rating": int(product.css("star-rating")), - need to select next class after star-rating
                # "category": ,- need to get from detail page. class"breadcrumb" and choose text from <a>
                # "description" - need to get from detail page,
                # "upc": ,-need to get from detail page
            }

            next_page = response.css(".next").css("a::attr(href)").get()
            print(f"Next_page_url: {next_page}")

            if next_page is not None:
                next_page_url = response.urljoin(next_page)
                yield scrapy.Request(next_page_url, callback=self.parse)
