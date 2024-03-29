import influxdb
import pymysql
import time

from scraper import get_data


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


while True:
    points = []

    for keyword in get_keywords():
        keyword = keyword[0]
        print(f'search word: {keyword}')
        price_data = get_data(keyword)
        data = {
            'measurement': 'price',
            'tags': {
                'name': keyword
            },
            'fields': price_data
        }
        points.append(data)

    try:
        db.write_points(points)
    except influxdb.exceptions.InfluxDBClientError:
        print('influx error', points)
    
    time.sleep(600)
