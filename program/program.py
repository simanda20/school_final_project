import re # import regex
from time import sleep # import sleep
import requests # import request
from bs4 import BeautifulSoup # import beautiful soup
import json # import json
import os # import os
from os.path import exists # checker of file existence
import logging # import logging
from datetime import datetime, timedelta # import datetime and delta time

def get_time_difference():
    """

    :return: float time difference
    """
    current_time = datetime.now() # get current time
    next_day = current_time + timedelta(days=1) # get next day
    next_day = next_day.replace(hour=1, minute=0, second=0, microsecond=0) # get first hour of next day
    time_difference = next_day - current_time # calculate time difference
    return time_difference.total_seconds() # convert time difference to seconds and return

def get_number(num):
    """

    :param num:
    :return: int
    """
    numbers_only = ""
    for c in num:
        if c.isnumeric():
            numbers_only += c # add every character if it is a digit

    return int(numbers_only) # return number

def get_pure_text(text):
    """

    :param text:
    :return:
    """
    text = text.replace("\n", "") # remove line breaks
    text = re.sub(r'\s+', '', text) # remove spaces
    return text

class Querry:
    """
        class representicng web querry
    """
    def __init__(self, _shop_name, _shop_url, _url, _starting_page, _page_offset, _product_box_class, _product_type):
        """

        :param _shop_name:
        :param _shop_url:
        :param _url:
        :param _starting_page:
        :param _page_offset:
        :param _product_box_class:
        :param _product_type:
        """
        self.shop_name = _shop_name  # shop name
        self.shop_url = _shop_url  # shop url
        self.url = _url  # prep url
        self.product_type = _product_type # product type
        self.starting_page = _starting_page # starting page
        self.page_offset = _page_offset # page offset
        self.product_box_class = _product_box_class # product box class
        self.app_token = 123456789  # token
        self.processed_products = [] # processed products
        self.send_on_url = "http://mujweb.simane.cz/actions/data_listener.php" # url for saving data

    def send_products(self):
        """

        :return:
        """
        try:
            req = requests.post( # send data on web
                url=self.send_on_url,
                data={
                    "token": self.app_token,
                    "data": json.dumps(self.processed_products)
                }
            )
            print(req.text)
        except Exception as e:
            print(e)

    def process_product(self, product):
        """

        :param product:
        """
        pass

    def main_loop(self):
        """

        :return:
        """
        has_products = True  # while checker
        page = self.starting_page  # page
        first_product = ""  # variable with first product

        while has_products:
            print(page)
            cur_url = self.url.replace("$page", str(page))  # current url address
            try:
                req = requests.get(cur_url)  # get request
                content = req.text  # get html of page

                soup = BeautifulSoup(content, "html.parser")  # create beautifulsoup

                body = soup.find("body")  # find html body

                products = body.find_all("div", {"class": self.product_box_class})  # get boxes

                if len(products) == 0:  # if we already seen all products break loop
                    has_products = False
                    break

                if first_product == "":  # if loop started, get first product to compare
                    first_product = products[0]

                for product in products:  # process all products
                    self.process_product(product)

                page += self.page_offset  # load new page

            except Exception as e:
                print(e)
                break

            sleep(5)  # anti block waiting

        self.send_products()

class Querry_Alza(Querry):
    """
        class representing web querry for Alza
    """
    def __init__(self, _link, _product_type):
        """

        :param _link:
        :param _product_type:
        """
        super().__init__(
            "Alza",
            "https://www.alza.cz",
            _link,
            1,
            1,
            "box",
            _product_type
        )

    def process_product(self, product):
        """

        :param product: html element of product with needed data
        :return:
        """
        try:
            product_name = product.find("a", {"class": "name"}).text  # get product name
            product_price_sep = product.find("span",{"class": "price-box__price"}).text  # get product price with separation
            product_price = get_number(product_price_sep) # get price
            product_code = product.get("data-code")  # code of product
            product_id = self.shop_name + product.get("data-id")  # product id used by eshop with shopname at start
            product_link = self.shop_url + product.find("a", {"class": "browsinglink"}).get("href")  # product link
            product_price_box = product.find("div", {"class": "price-box"}) # get pricebox
            product_price_box_classes = product_price_box.get("class") # get pricebox classes
            product_discount = "price-box--Discount" in product_price_box_classes # check if product has discount
            product_opened = product.get("data-almostnew") == "true" # check if is product new
            product_discount_percentage = 0
            product_price_before = product_price
            if product_discount:
                product_discount_percentage = get_number(product_price_box.find("span", {"class": "price-box__header-text"}).text) # discount in percentage
                product_price_before = get_number(product.find("span", {"class": "price-box__compare-price"}).text) # get price before discount

            self.processed_products.append({
                "name": product_name,
                "price": product_price,
                "code": product_code,
                "id": product_id,
                "link": product_link,
                "discount": product_discount,
                "discount_percentage": product_discount_percentage,
                "price_before": product_price_before,
                "opened": product_opened,
                "shop_name": self.shop_name,
                "shop_url": self.shop_url,
                "product_type": self.product_type
            })
            print(self.processed_products[-1])
        except Exception as e:
            print(e)

class Querry_CZC(Querry):
    """
        class representing web querry for CZC
    """
    def __init__(self, _link, _product_type):
        """

        :param _link:
        :param _product_type:
        """
        super().__init__(
            "CZC",
            "https://www.czc.cz",
            _link,
            0,
            27,
            "new-tile",
            _product_type
        )

    def process_product(self, product):
        """

        :param product: html element of product with needed data
        :return:
        """
        try:
            product_name = product.find("div", {"class": "overflow"}).find("a").text.split("\n")[0]  # get product name
            price_wrapper = product.find("div", {"class": "pd-price-wrapper"})
            product_price_sep = price_wrapper.find("span", {"class": "price-vatin"}).text  # get product price with separation
            product_price = get_number(product_price_sep)  # get price
            product_code = product.get("data-product-code")  # code of product
            product_id = self.shop_name + product.get("data-product-code")  # product id used by eshop with shopname at start
            product_link = self.shop_url + product.find("div", {"class": "overflow"}).find("a").get("href")  # product link
            product_discount = product.find("span", {"class": "price-before"}) is not None # check if product is in sale
            product_flags = [get_pure_text(x.get_text()) for x in product.find_all("div", {"class": "sticker"})] # find all stickers

            product_opened = ("zánovnízboží" in product_flags) or ("použitézboží" in product_flags) or ("rozbalenézboží" in product_flags) # check if was product opened or not
            product_discount_percentage = 0
            product_price_before = product_price
            if product_discount:
                price_before = product.find("span", {"class": "price-before"})
                product_price_before = get_number(price_before.find("span", {"class": "price-vatin"}).text) # get price before
                product_discount_percentage = 100 - ((product_price * 100) / product_price_before) # count discount percentage
                product_discount_percentage = int(round(product_discount_percentage)) # get round number

            self.processed_products.append({
                "name": product_name,
                "price": product_price,
                "code": product_code,
                "id": product_id,
                "link": product_link,
                "discount": product_discount,
                "discount_percentage": product_discount_percentage,
                "price_before": product_price_before,
                "opened": product_opened,
                "shop_name": self.shop_name,
                "shop_url": self.shop_url,
                "product_type": self.product_type
            })
            print(self.processed_products[-1])
        except Exception as e:
            print(e)

class Querry_Datart(Querry):
    """
        class representing web querry for Datart
    """
    def __init__(self , _link, _product_type):
        """

        :param _link:
        :param _product_type:
        """
        super().__init__(
            "Datart",
            "https://www.datart.cz",
            _link,
            1,
            1,
            "product-box",
            _product_type
        )

    def process_product(self, product):
        """

        :param product:
        :return:
        """
        try:
            product_name = product.find("div", {"class": "item-title-holder"}).find("a").text  # get product name
            product_price_sep = product.find("div", {"class": "actual"}).text  # get product price with separation
            product_price = get_number(product_price_sep) # get price
            product_code = json.loads(product.get("data-track"))["id"]  # code of product
            product_id = self.shop_name + json.loads(product.get("data-track"))["id"]  # product id used by eshop with shopname at start
            product_link = self.shop_url + product.find("div", {"class": "item-title-holder"}).find("a").get("href")  # product link
            product_discount = product.find("span", {"class": "query-icon"}) is not None # check if product has a discount
            product_opened = "Zánovní" in [x.get_text() for x in product.find_all("span", {"class": "flag"})] # check if was product opened or not
            product_discount_percentage = 0
            product_price_before = product_price
            if product_discount:
                price_before = product.find("span", {"class": "cut-price"})
                product_price_before = get_number(price_before.find("del").text) # get price before discount
                product_discount_percentage = 100 - ((product_price * 100) / product_price_before) # count discount percentage
                product_discount_percentage = int(round(product_discount_percentage)) # get round number

            self.processed_products.append({
                "name": product_name,
                "price": product_price,
                "code": product_code,
                "id": product_id,
                "link": product_link,
                "discount": product_discount,
                "discount_percentage": product_discount_percentage,
                "price_before": product_price_before,
                "opened": product_opened,
                "shop_name": self.shop_name,
                "shop_url": self.shop_url,
                "product_type": self.product_type
            })
            print(self.processed_products[-1])
        except Exception as e:
            print(e)

run = True
while run:
    if exists("pages.csv"):  # check existention of shop configuration file
        sites = []
        querries = []
        with open("pages.csv", "r") as file:  # open file and read data
            sites = file.readlines()
            file.close()

        if len(sites) > 0:  # if are there any data
            for site in sites:
                site = site.split(";")  # initialize querries
                match site[0]:
                    case "Alza":
                        querries.append(Querry_Alza(site[2].replace("\n", ""), site[1]))  # create new alza querry
                    case "CZC":
                        querries.append(Querry_CZC(site[2].replace("\n", ""), site[1]))  # create new CZC querry
                    case "Datart":
                        querries.append(Querry_Datart(site[2].replace("\n", ""), site[1]))  # create new Datart querry
                    case _:
                        print("Unknown querry")  # else

            if len(querries) > 0:
                for querry in querries:  # start all querries
                    querry.main_loop()

                sleep(get_time_difference())  # repeat every day at 1AM
            else:
                print("File has not any valid quarries.")
                print("Please add your shops in csv format and start app again.")
                print("ShopName;ProductType;SearchedLink with $page pointer.")
                run = False
                input("Press ENTER to exit")
        else:
            print("File has not data inside.")
            print("Please add your shops in csv format and start app again.")
            print("ShopName;ProductType;SearchedLink with $page pointer.")
            run = False
            input("Press ENTER to exit")
    else:
        with open("pages.csv", "x") as file:  # create file if not exist
            file.write("")
            print("File 'pages.csv' had been created.")
            print("Please add your shops in csv format and start app again.")
            print("ShopName;ProductType;SearchedLink with $page pointer.")
            file.close()
        run = False
        input("Press ENTER to exit")
