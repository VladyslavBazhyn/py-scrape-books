from pathlib import Path

import scrapy
from scrapy import Spider, Selector
from scrapy.http import Response

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from twisted.internet.defer import Deferred


options = Options()

options.add_argument("--headless")
options.add_argument("--disable-gpu")


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome(options=options)

    def close(self: Spider, reason: str) -> Deferred[None] | None:
        self.driver.close()
        return super().close(spider=self, reason=reason)

    def parse(self, response: Response, **kwargs):
        for product in response.css(".product_pod"):

            detail_book_url = response.urljoin(product.css(".image_container").css("a::attr(href)").get())
            detailed_info = self._parse_detailed_info(detail_book_url=detail_book_url)

            yield {
                "title": product.css("h3").css("a::attr(title)").get(),
                "price": float(product.css(".price_color::text").get()[1:]),
                "amount_in_stock": detailed_info["amount_in_stock"],
                "rating": detailed_info["rating"],
                "category": detailed_info["category"],
                "description": detailed_info["description"],
                "upc": detailed_info["upc"]
            }

            next_page = response.css(".next").css("a::attr(href)").get()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def _parse_detailed_info(self, detail_book_url: str) -> dict:
        self.driver.get(detail_book_url)

        amount_in_stock = int(self.driver.find_element(By.CLASS_NAME, "availability").text.split(" ")[-2][1:])

        rating_element = self.driver.find_element(By.CLASS_NAME, "star-rating")
        rating = rating_element.get_attribute("class").split(" ")[-1]

        category = self.driver.find_element(
            By.CLASS_NAME, "breadcrumb"
        ).find_elements(
            By.CSS_SELECTOR, "li"
        )[-2].find_element(By.CSS_SELECTOR, "a").text

        description = self.driver.find_elements(By.CSS_SELECTOR, "p")[3].text

        upc = self.driver.find_element(
            By.CLASS_NAME, "table"
        ).find_element(By.CSS_SELECTOR, "td").text

        detailed_info = {
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc
        }
        return detailed_info
