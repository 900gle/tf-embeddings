# -*- coding: utf-8 -*-
import time
import json

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

def run_query_loop(keyword):
    for i in range(1, 200):
        sql = query_a(i, keyword)
        time.sleep(7)
        # cur.execute(sql)
        # rows = cur.fetchall()
        print(i)


def query_a(index, keyword):
    # https://search.tmon.co.kr/api/search/v4/deals?_=1703425774300&keyword=%EB%A3%A8%EC%9D%B4%EB%B9%84%ED%86%B5&mainDealOnly=true&optionDealOnly=false&page=1&showFilter=true&size=60&sortType=POPULAR&thr=hs&useTypoCorrection=true

    url_api = "https://search.tmon.co.kr/api/search/v4/deals?_=1703425774300&keyword=" + keyword + "&mainDealOnly=true&optionDealOnly=false&page=" + str(
        index) + "&showFilter=true&size=100&sortType=POPULAR&thr=hs&useTypoCorrection=true"

    response = requests.get(url_api, verify=False)
    json_data = json.loads(response.text)

    keyword = str(json_data["data"]["searchKeyword"])

    for deal in json_data["data"]["searchDeals"]:
        title_name = str(deal["searchDealResponse"]["dealInfo"]["titleName"])
        name = "\\'".join(title_name.split("'"))
        vector = embed_text(name)[0]
        price = str(deal["searchDealResponse"]["dealInfo"]["priceInfo"]["price"])
        image = str(deal["searchDealResponse"]["dealInfo"]["imageInfo"]["pc3ColImageUrl"])
        sql = "INSERT INTO goods_tmon ( keyword, name, price, weight, popular, image, feature_vector, type ) VALUES ('" + keyword + "','" + name + "'," +price+",0.1,1, '"+image+"','"+ str(vector)+"', 'T');"
        cur.execute(sql)
    print(sql)

    return sql


##### EMBEDDING #####
def embed_text(name):
    print(name)
    vectors = model(name)
    return [vector.numpy().tolist() for vector in vectors]


##### MAIN SCRIPT #####

if __name__ == '__main__':
    print("Downloading pre-trained embeddings from tensorflow hub...")
    model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")
    COUNTRY_FILE = "./keyword.csv"

    with open(COUNTRY_FILE) as data_file:
        for line in data_file:
            line = line.strip()
            print(line)
            run_query_loop(line)

    print("Done.")


