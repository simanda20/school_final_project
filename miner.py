import re  # import regex
from time import sleep  # import sleep
import requests  # import request
from bs4 import BeautifulSoup  # import beautiful soup
import json  # import json
import logging  # import logging


class Miner:
    """
        class representing web data miner
    """

    def __init__(
            self,
            _shop_name,
            _shop_url,
            _url,
            _starting_page,
            _page_offset,
            _product_box_class,
            _product_type,
            _app_token,
            _send_on_url
    ):
        """
        Constructor of data miner
        :param _shop_name: string with name of shop
        :param _shop_url: string with url of shop
        :param _url: string with searched url and $page pointer
        :param _starting_page: int with starting page
        :param _page_offset: int with page offset
        :param _product_box_class: string with class of product box on page
        :param _product_type: string with product type for db
        """
        self.shop_name = _shop_name  # shop name
        self.shop_url = _shop_url  # shop url
        self.url = _url  # prep url
        self.product_type = _product_type  # product type
        self.starting_page = _starting_page  # starting page
        self.page_offset = _page_offset  # page offset
        self.product_box_class = _product_box_class  # product box class
        self.app_token = _app_token  # token
        self.processed_products = []  # processed products
        self.send_on_url = _send_on_url  # url for saving data

    @staticmethod
    def get_number(num):
        """
        Gets pure number from string
        :param num: string with seeked number
        :return: int searched number
        """
        numbers_only = ""
        for c in num:
            if c.isnumeric():
                numbers_only += c  # add every character if it is a digit

        return int(numbers_only)  # return number

    @staticmethod
    def get_pure_text(text):
        """
        Replaces line breaks and spaces
        :param text: string with line breaks and spaces
        :return: string without line breaks and spaces
        """
        text = text.replace("\n", "")  # remove line breaks
        text = re.sub(r'\s+', '', text)  # remove spaces
        return text

    def send_products(self):
        """
        Sends data on web service
        """
        if len(self.processed_products) > 0:
            try:
                req = requests.post(  # send data on web
                    url=self.send_on_url,
                    data={
                        "token": self.app_token,
                        "data": json.dumps(self.processed_products)
                    }
                )
                self.processed_products.clear()  # clear processed products
                if req.status_code in range(200, 300):  # check server response
                    returned_data = req.json()
                    if returned_data["access"]:  # access granted
                        print("Service processed data successfully")
                    else:  # service error
                        logging.error("Service responded with: " + returned_data["error"]["error_code"] + " " +
                                      returned_data["error"]["error_message"])
                else:  # negative response from server
                    print("Service response: " + str(req.status_code) + " " + req.text)
                    logging.error("Service response: " + str(req.status_code) + " " + req.text)

            except requests.exceptions.ConnectionError:  # handle no internet connection
                print("Connection to the internet was lost")
                logging.error("No internet connection")

            except Exception as e:
                print(e)
                logging.error("While sending data to service: " + str(e))

        else:
            logging.error("There are not any processed products to send")

    def send_problem(self):
        """
        Sends information about error on web service
        """
        logging.info("Sending error to web service")
        try:
            req = requests.post(
                url=self.send_on_url,
                data={
                    "token": self.app_token,
                    "error": self.shop_name
                }
            )
            if req.status_code in range(200, 300):  # check server response
                returned_data = json.loads(req.text)
                if returned_data["access"]:  # access granted
                    logging.info("Service saved information about error successfully")
                else:  # service error
                    logging.error(
                        "Service responded with: " + returned_data["error"]["error_code"] + " " +
                        returned_data["error"][
                            "error_message"])
            else:  # server negative response
                logging.error("Service response: " + str(req.status_code) + " " + req.text)

        except requests.exceptions.ConnectionError:  # handle no internet connection
            print("Connection to the internet was lost")
            logging.error("No internet connection")

        except Exception as e:
            print(e)
            logging.error("Unknown exception: " + str(e))

    def process_product(self, product):
        """
        Process given product and gets data from it. For each shop is this method different
        :param product: string with html structure of product
        """
        pass

    def main_loop(self, _sleeping_between_requests_seconds):
        """
        Data scraper loading all products from page
        """
        has_products = True  # while checker
        page = self.starting_page  # page
        first_product = ""  # variable with first product

        while has_products:
            print(page)
            cur_url = self.url.replace("$page", str(page))  # current url address
            try:
                req = requests.get(cur_url)  # get request
                if req.status_code in range(200, 300):
                    content = req.text  # get html of page

                    soup = BeautifulSoup(content, "html.parser")  # create beautifulsoup

                    body = soup.find("body")  # find html body

                    products = body.find_all("div", {"class": self.product_box_class})  # get boxes

                    if len(products) == 0:  # if we have already seen all products break loop
                        has_products = False
                        break

                    if first_product == "":  # if loop started, get first product to compare
                        first_product = products[0]

                    for product in products:  # process all products
                        self.process_product(product)

                    page += self.page_offset  # load new page

                elif req.status_code in range(400, 500):
                    print("Invalid request on the server. Please check searching url.")
                    logging.error("Invalid request on the server. " + str(req.status_code))
                    break

                elif req.status_code in range(500, 600):
                    print("Server was unable to handle request. " + str(req.status_code))
                    logging.error("Server was unable to handle request. " + str(req.status_code))
                    self.send_problem()  # send information about problem
                    break

                else:
                    print("Unexpected status code: " + str(req.status_code))
                    logging.error("Unexpected status code. " + str(req.status_code))
                    self.send_problem()  # send information about problem
                    break

            except requests.exceptions.ConnectionError:  # handle connection
                print("Unable to connect. We will try it again later")
                logging.error("Unable to connect to server")
                self.send_problem()
                break

            except Exception as e:
                print(e)
                logging.error("While processing page: " + str(e))
                self.send_problem()  # send information about problem
                break

            self.send_products()  # send products
            sleep(_sleeping_between_requests_seconds)  # anti block waiting


class MinerAlza(Miner):
    """
        class representing web data miner for Alza
    """

    def __init__(self, _link, _product_type, _app_token, _send_on_url):
        """
        Constructor of alza data miner
        :param _link: string with searched url and $page pointer
        :param _product_type: string with product type
        """
        super().__init__(
            "Alza",
            "https://www.alza.cz",
            _link,
            1,
            1,
            "box",
            _product_type,
            _app_token,
            _send_on_url
        )

    def process_product(self, product):
        """
        Process given product and gets data from it. Used for alza html structure
        :param product: string with html structure of product
        """
        try:
            product_name = product.find("a", {"class": "name"}).text  # get product name
            product_price_sep = product.find("span",
                                             {"class": "price-box__price"}).text  # get product price with separation
            product_price = self.get_number(product_price_sep)  # get price
            product_code = product.get("data-code")  # code of product
            product_id = self.shop_name + product.get("data-id")  # product id used by eshop with shop name at start
            product_link = self.shop_url + product.find("a", {"class": "browsinglink"}).get("href")  # product link
            product_price_box = product.find("div", {"class": "price-box"})  # get pricebox
            product_price_box_classes = product_price_box.get("class")  # get pricebox classes
            product_discount = "price-box--Discount" in product_price_box_classes or "price-box--BlackFriday" in product_price_box_classes # check if product has discount
            product_opened = product.get("data-almostnew") == "true"  # check if is product new
            product_discount_percentage = 0
            product_price_before = product_price
            if product_discount:
                check_if_percentage_avalible = "%" in product_price_box.find("span", {
                    "class": "price-box__header-text"}).text  # check if data about discount avalible
                if check_if_percentage_avalible:
                    product_discount_percentage = self.get_number(product_price_box.find("span", {
                        "class": "price-box__header-text"}).text)  # discount in percentage
                    product_price_before = self.get_number(
                        product.find("span", {"class": "price-box__compare-price"}).text)  # get price before discount
                else:
                    product_discount = check_if_percentage_avalible

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
            logging.warning("While processing product: " + str(e))


class MinerCZC(Miner):
    """
        class representing web data miner for CZC
    """

    def __init__(self, _link, _product_type, _app_token, _send_on_url):
        """
        Constructor of CZC data miner
        :param _link: string with searched url and $page pointer
        :param _product_type: string with product type
        """
        super().__init__(
            "CZC",
            "https://www.czc.cz",
            _link,
            0,
            27,
            "new-tile",
            _product_type,
            _app_token,
            _send_on_url
        )

    def process_product(self, product):
        """
        Process given product and gets data from it. Used for CZC html structure
        :param product: string with html structure of product
        """
        try:
            product_name = product.find("div", {"class": "overflow"}).find("a").text.split("\n")[0]  # get product name
            price_wrapper = product.find("div", {"class": "pd-price-wrapper"})
            product_price_sep = price_wrapper.find("span",
                                                   {"class": "price-vatin"}).text  # get product price with separation
            product_price = self.get_number(product_price_sep)  # get price
            product_code = product.get("data-product-code")  # code of product
            product_id = self.shop_name + product.get(
                "data-product-code")  # product id used by eshop with shopname at start
            product_link = self.shop_url + product.find("div", {"class": "overflow"}).find("a").get(
                "href")  # product link
            product_discount = product.find("span",
                                            {"class": "price-before"}) is not None  # check if product is in sale
            product_flags = [self.get_pure_text(x.get_text()) for x in
                             product.find_all("div", {"class": "sticker"})]  # find all stickers
            product_opened = ("zánovnízboží" in product_flags) or ("použitézboží" in product_flags) or (
                        "rozbalenézboží" in product_flags)  # check if was product opened or not
            product_discount_percentage = 0
            product_price_before = product_price
            if product_discount:
                price_before = product.find("span", {"class": "price-before"})
                product_price_before = self.get_number(
                    price_before.find("span", {"class": "price-vatin"}).text)  # get price before
                product_discount_percentage = 100 - (
                            (product_price * 100) / product_price_before)  # count discount percentage
                product_discount_percentage = int(round(product_discount_percentage))  # get round number

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
            logging.warning("While processing product: " + str(e))
            print(e)


class MinerDatart(Miner):
    """
        class representing web data miner for Datart
    """

    def __init__(self, _link, _product_type, _app_token, _send_on_url):
        """
        Constructor of Datart data miner
        :param _link: string with searched url and $page pointer
        :param _product_type: string with product type
        """
        super().__init__(
            "Datart",
            "https://www.datart.cz",
            _link,
            1,
            1,
            "product-box",
            _product_type,
            _app_token,
            _send_on_url
        )

    def process_product(self, product):
        """
        Process given product and gets data from it. Used for datart html structure
        :param product: string with html structure of product
        """
        try:
            product_name_container = product.find("div", {"class": "item-title-holder"})  # get product name
            if product_name_container is not None:  # check if product is not just ad
                product_name = product_name_container.find("a").text
                product_price_sep = product.find("div", {"class": "actual"}).text  # get product price with separation
                product_price = self.get_number(product_price_sep)  # get price
                product_code = json.loads(product.get("data-track"))["id"]  # code of product
                product_id = self.shop_name + json.loads(product.get("data-track"))[
                    "id"]  # product id used by eshop with shopname at start
                product_link = self.shop_url + product.find("div", {"class": "item-title-holder"}).find("a").get(
                    "href")  # product link
                product_discount = product.find("span",
                                                {"class": "query-icon"}) is not None  # check if product has a discount
                product_opened = "Zánovní" in [x.get_text() for x in product.find_all("span", {
                    "class": "flag"})]  # check if was product opened or not
                product_discount_percentage = 0
                product_price_before = product_price
                if product_discount:
                    price_before = product.find("span", {"class": "cut-price"})
                    product_price_before = self.get_number(price_before.find("del").text)  # get price before discount
                    product_discount_percentage = 100 - (
                            (product_price * 100) / product_price_before)  # count discount percentage
                    product_discount_percentage = int(round(product_discount_percentage))  # get round number

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
            else:
                print("Product is just ad.")

        except Exception as e:
            logging.warning("While processing product: " + str(e))
            print(e)
