import re # import regex
from time import sleep # import sleep
import requests # import request
from bs4 import BeautifulSoup # import beautiful soup
import json # import json

class Querry:
    """
        class representing web querry
    """
    def __init__(self):
        self.__shop_name = "Datart"  # shop name
        self.__shop_url = "https://www.datart.cz"  # shop url
        self.__url = "https://www.datart.cz/mobilni-telefony.html?showPage&page=$page&limit=16"  # prep url
        self.__app_token = 123456789  # token
        self.__processed_products = [] # processed products

    def __send_products(self):
        req = requests.post(
            url = "http://127.0.0.1/webScraping/actions/data_listener.php",
            data = {
                "token": self.__app_token,
                "data": json.dumps(self.__processed_products)
            }
        )
        print(req.text)



    def __process_product(self, product):
        try:
            product_name = product.find("div", {"class": "item-title-holder"}).find("a").text  # get product name
            product_price_sep = product.find("div", {"class": "actual"}).text  # get product price with separation
            product_price_not_sep = re.sub(r'\s+', '', product_price_sep)  # get product price without separation
            product_price = int(
                product_price_not_sep.replace("Kč", ""))  # get rid of ',-' or 'Kč' and get int from product price
            product_code = json.loads(product.get("data-track"))["id"]  # code of product
            product_id = self.__shop_name + json.loads(product.get("data-track"))[
                "id"]  # product id used by eshop with shopname at start
            product_link = self.__shop_url + product.find("div", {"class": "item-title-holder"}).find("a").get(
                "href")  # product link

            self.__processed_products.append({
                "name": product_name,
                "price": product_price,
                "code": product_code,
                "id": product_id,
                "link": product_link,
                "shop_name": self.__shop_name,
                "shop_url": self.__shop_url,
            })
            print(self.__processed_products[-1])
        except Exception as e:
            print(e)


    def main_loop(self):
        has_products = True  # while checker
        page = 1  # page
        first_product = ""  # variable with first product

        while has_products:
            print(page)
            cur_url = self.__url.replace("$page", str(page))  # current url address
            req = requests.get(cur_url)  # get request
            content = req.text  # get html of page

            soup = BeautifulSoup(content, "html.parser")  # create beautifulsoup

            body = soup.find("body")  # find html body

            products = body.find_all("div", {"class": "product-box"})  # get boxes

            if len(products) == 0 or first_product == products[0]:  # if we already seen all products break loop
                has_products = False
                break

            if first_product == "":  # if loop started, get first product to compare
                first_product = products[0]

            for product in products:  # process all products
                self.__process_product(product)

            page += 1 # load new page

            sleep(5)  # anti block waiting

        self.__send_products()

alza_querry = Querry()
alza_querry.main_loop()
