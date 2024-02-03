# -*- coding: utf-8 -*-
import time
import json

import matplotlib.pyplot as plt
import numpy as np

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import requests
import ssl
import urllib3
from time import sleep
from urllib import parse

print(ssl.OPENSSL_VERSION)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
f_v = open("./data/lazy_keyword.txt", 'w')


def csv_data():
    time = []
    query_cache = []
    request_cache = []

    with open(CSV_FILE) as data_file:
        for line in data_file:
            line = parse.quote(line.strip())
            time.append(query_a(line))
            q, r = cache_monitoring()
            query_cache.append(q)
            request_cache.append(r)

    print("api time 평균 : " + str(round(np.mean(time), 2)))
    plt.rcParams['font.family'] = 'AppleGothic'
    #
    # y = range(0, len(time))
    # x = time


    t = range(0, len(time))
    plt.rcParams['font.family'] = 'AppleGothic'

    fs = 1
    y = time

    # Plot the raw time series
    fig, axs = plt.figure(layout="constrained").subplot_mosaic([
        ['time', 'time'],
        ['query', 'request'],
    ])

    axs['time'].plot(t, y, lw=lw)
    axs['time'].set_xlabel(str(len(time)) + '회')
    axs['time'].set_ylabel('Time(ms)')

    axs['query'].plot(t, query_cache, lw=lw)
    axs['query'].set_ylabel('query')


    # Plot the PSD with different amounts of overlap between blocks
    axs['request'].plot(t, request_cache, lw=lw)
    axs['request'].set_ylabel('')
    axs['request'].set_title('request')

    for title, ax in axs.items():
        if title == 'time':
            continue

        ax.set_title(title)
        ax.sharex(axs['query'])
        ax.sharey(axs['query'])

    plt.show()




def query_a(keyword):

    with open(QUERY) as index_file:
        script_query = index_file.read().strip()
        script_query = script_query.replace("{keyword}", str(keyword))

    response = client.search(
        index=INDEX,
        body=script_query
    )

    search_time = response["took"]

    # print(search_time)

    if (search_time > 200):
        f_v.write(keyword + " 실행시간 : " + str(round(np.mean(search_time), 2)) + " (ms)\n")
        # f_v.write(parse.unquote(keyword)+ "\n")
    return search_time


def cache_monitoring():
    data = client.nodes.stats()
    node1 = data["nodes"]["bpumm1NjRAiDyuAgBN6XpQ"]["indices"]
    return node1["query_cache"]["memory_size_in_bytes"] / div, node1["request_cache"]["memory_size_in_bytes"] / div


def query_cache_monitoring():
    data = client.indices.stats()
    shop = data["indices"]["shop-2023-10-07-20"]["primaries"]["query_cache"] / div
    location = data["indices"]["location-index"]["primaries"]["query_cache"] / div
    return shop, location

def request_cache_monitoring():
    data = client.indices.stats()
    shop = data["indices"]["shop-2023-10-07-20"]["primaries"]["request_cache"] / div
    location = data["indices"]["location-index"]["primaries"]["request_cache"] / div
    return  shop / location

##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX = "location"
    CSV_FILE = "./data/country.csv"
    QUERY = "./query/cache_query.json"
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    # query_cache_monitoring()

    # client.indices.clear_cache()
    div = 100000
    lw = 0.7
    csv_data()
    f_v.close()

    print("Done.")
