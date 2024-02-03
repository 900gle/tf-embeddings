# -*- coding: utf-8 -*-
import time
import json
from datetime import datetime, timedelta
import random

import requests
import ssl
import urllib3
import pymysql

from time import sleep


import tensorflow_hub as hub
import tensorflow_text

import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
import numpy as np

print(ssl.OPENSSL_VERSION)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


con = pymysql.connect(host='localhost', user='ldh', password='doo',
                      db='shop', charset='utf8',  # 한글처리 (charset = 'utf8')
                      autocommit=True,  # 결과 DB 반영 (Insert or update)
                      cursorclass=pymysql.cursors.DictCursor  # DB조회시 컬럼명을 동시에 보여줌
                      )
cur = con.cursor()


##### SEARCHING #####
def tmon_data():

    now = datetime.now()

    sql = "select  min(id) as min , max(id) as max  from goods_tmon"
    cur.execute(sql)
    row = cur.fetchone()

    start = row['min']
    end = row['max'] + 1
    size = 100

    for i in range(start, end, size):

        h = random.randint(1,1000)
        m = random.randint(1,1000)
        new_date = now - timedelta( hours= h , minutes= m)

        sql = "select * from goods_tmon where id > %s and id < %s"
        param = (i, i + size)
        print(param)
        cur.execute(sql,param)
        data = cur.fetchall()
        for r in data:
            insert_sql = "INSERT INTO aqqle_goods ( keyword, name, price, weight, popular, image, feature_vector, type, created_time ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            insert_param = (r['keyword'], r['name'], r['price'], r['weight'],r['popular'],r['image'],r['feature_vector'],r['type'], new_date )
            cur.execute(insert_sql,insert_param)

def naver_data():
    now = datetime.now()
    sql = "select  min(id) as min , max(id) as max  from goods_naver"
    cur.execute(sql)
    row = cur.fetchone()

    start = row['min']
    end = row['max'] + 1
    size = 100

    h = random.randint(1,1000)
    m = random.randint(1,1000)
    new_date = now - timedelta( hours= h , minutes= m)

    for i in range(start, end, size):
        sql = "select keyword,brand, category,category1, category2, category3, category4, category5 ,name, price, weight, popular, image, feature_vector, type from goods_naver where id > %s and id < %s"
        param = (i, i + size)
        print(param)
        cur.execute(sql,param)
        data = cur.fetchall()
        for r in data:
            insert_sql = "INSERT INTO aqqle_goods ( keyword,brand, category,category1, category2, category3, category4, category5 ,name, price, weight, popular, image, feature_vector, type, created_time ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            insert_param = (r['keyword'], r['brand'], r['category'], r['category1'], r['category2'], r['category3'], r['category4'], r['category5'], r['name'], r['price'], r['weight'],r['popular'],r['image'],r['feature_vector'],'N', new_date )
            cur.execute(insert_sql,insert_param)


##### MAIN SCRIPT #####

if __name__ == '__main__':
    tmon_data()
    naver_data()
    print("Done.")


