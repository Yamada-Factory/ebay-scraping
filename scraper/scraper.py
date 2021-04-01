import re
import requests
from bs4 import BeautifulSoup

PRICE_PETTERN = re.compile('\d{1,3}(,\d{3})*')

def get_data(keyword):
    html = requests.get(f'https://www.ebay.com/sch/i.html?_nkw={keyword}&_sop=12').text
    soup = BeautifulSoup(html, 'html.parser')

    price_data_list = []
    items = soup.select('.s-item__info.clearfix')
    # print(len(items))
    for i, item in enumerate(items):
        try:
            url = item.select_one('.s-item__link').get('href')
            name = item.select_one('.s-item__title').string
        except AttributeError:
            continue
        if name == None:
            name = list(item.select_one('.s-item__title').children)[1].string

        price = item.select_one('.s-item__price').string
        try:
            shipping = item.select_one('.s-item__logisticsCost').string
        except AttributeError:
            continue

        try:
            price = int(PRICE_PETTERN.search(price).group().replace(',', ''))
        except TypeError:
            continue
        try:
            shipping = int(PRICE_PETTERN.search(shipping).group().replace(',', ''))
        except AttributeError:
            shipping = 0
        
        # print(name, price, shipping, price+shipping)

        data = (price+shipping, price, shipping, name, url)
        price_data_list.append(data)

    lowest = min(price_data_list, key=lambda x: x[0])
    # lowest = price_data_list[0]
    # print(lowest)

    return {
        'price': lowest[1],
        'shpping': lowest[2],
        'sum': lowest[0],
        'url': lowest[4],
        'title': lowest[3],
    }
