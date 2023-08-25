import re # import regex
from time import sleep # import sleep
import requests # import request
from bs4 import BeautifulSoup # import beautiful soup

def process_product(product):
    product_name = product.find("a", {"class": "name"}).text # get product name
    product_price_sep = product.find("span", {"class": "price-box__price"}).text # get product price with separation
    product_price_not_sep = re.sub(r'\s+', '', product_price_sep) # get product price without separation
    product_price = int(product_price_not_sep.replace(",-", "")) # get rid of ',-' and get int from product price
    product_code = product.get("data-code") # code of product
    product_id = product.get("data-id") # product id used by eshop

url = "https://www.alza.cz/televize/18849604-p$page.htm" # prep url
page = 1 # page
has_products = True # while checker
first_product = "" # variable with first product

while has_products: # querry
    cur_url = url.replace("$page", str(page)) # current url address
    req = requests.get(cur_url)  # get request
    content = req.text  # get html of page

    soup = BeautifulSoup(content, "html.parser")  # create beautifulsoup

    body = soup.find("body")  # find html body

    products = body.find_all("div", {"class": "box"})  # get boxes

    if len(products) == 0: # if we already seen all products break loop
        has_products = False
        break

    if first_product == "":  # if loop started, get first product to compare
       first_product = products[0]

    for product in products: # process all products
        process_product(product)

    page += 1 # load new page

    sleep(5) # anti block waiting
