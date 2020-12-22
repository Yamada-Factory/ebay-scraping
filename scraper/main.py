import requests
from bs4 import BeautifulSoup
import influxdb
import pymysql
import time

import re


sqldb = pymysql.connect(user = 'root', password = 'root', db = 'ebay', host = 'sqldb', port=3306)
print('connected sqldb')

db = influxdb.InfluxDBClient(host='influxdb', port=8086, username='root', password='root', database='ebay')
print('connected influxdb')


def get_keywords():
    with sqldb.cursor() as cursor:
        cursor.execute("SELECT word FROM items WHERE word != ''")
        result = cursor.fetchall()
        sqldb.commit()
    return result


PRICE_PETTERN = re.compile('\d{1,3}(,\d{3})*')

def get_data(keyword):
    html = requests.get(f'https://www.ebay.com/sch/i.html?_nkw={keyword}&_sop=12').text
    soup = BeautifulSoup(html, 'html.parser')

    price_data_list = []
    items = soup.select('.s-item__info.clearfix')
    for item in items:
        url = item.select_one('.s-item__link').get('href')
        name = item.select_one('.s-item__title').string
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
        'measurement': 'price',
        'tags': {
            'name': keyword
        },
        'fields': {
            'price': lowest[1],
            'shpping': lowest[2],
            'sum': lowest[0],
            'url': lowest[4],
            'title': lowest[3],
        }
    }


print('start')
while True:
    points = []

    for keyword in get_keywords():
        data = get_data(keyword[0])
        points.append(data)

    db.write_points(points)
    
    time.sleep(600)
