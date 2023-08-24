from time import sleep # import sleep
import requests # import request
from bs4 import BeautifulSoup # import beautiful soup

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
        # process_product(product)
        print(product.find("a", {"class": "name"}).text + "      price: " + product.find("span", {"class": "price-box__price"}).text.replace("&nbsp;", " "))
        continue

    page += 1 # load new page

    sleep(5) # anti block waiting
