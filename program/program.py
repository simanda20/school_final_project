import re # import regex
from time import sleep # import sleep
import requests # import request
from bs4 import BeautifulSoup # import beautiful soup
import json # import json

class Querry:
    """
        class representicng web querry
    """

    def __init__(self, _shop_name, _shop_url, _url, _starting_page, _page_offset, _product_box_class):
        self.shop_name = _shop_name  # shop name
        self.shop_url = _shop_url  # shop url
        self.url = _url  # prep url
        self.starting_page = _starting_page # starting page
        self.page_offset = _page_offset # page offset
        self.produt_box_class = _product_box_class # product box class
        self.app_token = 123456789  # token
        self.processed_products = [] # processed products

    def send_products(self):
        req = requests.post(
            url = "http://127.0.0.1/webScraping/actions/data_listener.php",
            data = {
                "token": self.app_token,
                "data": json.dumps(self.processed_products)
            }
        )
        print(req.text)

    def process_product(self, product):
        pass

    def main_loop(self):
        has_products = True  # while checker
        page = self.starting_page  # page
        first_product = ""  # variable with first product

        while has_products:
            print(page)
            cur_url = self.url.replace("$page", str(page))  # current url address
            req = requests.get(cur_url)  # get request
            content = req.text  # get html of page

            soup = BeautifulSoup(content, "html.parser")  # create beautifulsoup

            body = soup.find("body")  # find html body

            products = body.find_all("div", {"class": self.produt_box_class})  # get boxes

            if len(products) == 0:  # if we already seen all products break loop
                has_products = False
                break

            if first_product == "":  # if loop started, get first product to compare
                first_product = products[0]

            for product in products:  # process all products
                self.process_product(product)

            page += self.page_offset  # load new page

            sleep(5)  # anti block waiting

        self.send_products()



class Querry_Alza(Querry):
    """
        class representing web querry for Alza
    """
    def __init__(self):
        super().__init__("Alza", "https://www.alza.cz", "https://www.alza.cz/televize/18849604-p$page.htm", 1, 1, "box")

    def process_product(self, product):
        product_name = product.find("a", {"class": "name"}).text # get product name
        product_price_sep = product.find("span", {"class": "price-box__price"}).text # get product price with separation
        product_price_not_sep = re.sub(r'\s+', '', product_price_sep) # get product price without separation
        product_price = int(product_price_not_sep.replace(",-", "")) # get rid of ',-' and get int from product price
        product_code = product.get("data-code") # code of product
        product_id = self.shop_name + product.get("data-id") # product id used by eshop with shopname at start
        product_link = self.shop_url + product.find("a", {"class": "browsinglink"}).get("href") # product link

        self.processed_products.append({
            "name": product_name,
            "price": product_price,
            "code": product_code,
            "id": product_id,
            "link": product_link,
            "shop_name": self.shop_name,
            "shop_url": self.shop_url,
        })
        print(self.processed_products[-1])

alza_querry = Querry_Alza()
alza_querry.main_loop()
