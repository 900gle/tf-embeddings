# -*- coding: utf-8 -*-
import time

import requests
import ssl
import urllib3
import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
import numpy as np

print(ssl.OPENSSL_VERSION)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##### SEARCHING #####

def run_query_loop():
    time_a = []
    query_c = []
    request_c = []

    with open(COUNTRY_FILE) as data_file:
        for line in data_file:
            line = line.strip()
            time_a.append(query_a(line))
            query_cache, request_cache = cache_monitoring()
            query_c.append(query_cache)
            request_c.append(request_cache)

    print("API 평균 : " + str(round(np.mean(time_a), 2)))

    t = range(0, len(time_a))
    plt.rcParams['font.family'] = 'AppleGothic'

    fig, ax = plt.subplots()
    ax.set_title('API cache')
    line1, = ax.plot(t, time_a, lw=2, label='Time')
    line2, = ax.plot(t, query_c, lw=2, label='Query c')
    line3, = ax.plot(t, request_c, lw=2, label='Request c')
    leg = ax.legend(loc='upper right', fancybox=False, shadow=False)

    ax.set_ylabel('time')
    ax.set_xlabel('query' + str(len(time_a)))

    lines = [line1, line2, line3]
    lined = {}
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(True)  # Enable picking on the legend line.
        lined[legline] = origline

    def on_pick(event):
        legline = event.artist
        origline = lined[legline]
        visible = not origline.get_visible()
        origline.set_visible(visible)
        legline.set_alpha(1.0 if visible else 0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', on_pick)
    plt.show()


def query_a(keyword):
    search_start = time.time()
    url_api = "http://localhost:8080/api/search/shop?searchWord="+keyword+"&similarity=N&from=0&size=10"
    response_api = requests.get(url_api, verify=False)
    search_time = time.time() - search_start
    return search_time * 1000


def cache_monitoring():
    data = client.nodes.stats()
    node = data["nodes"]["bpumm1NjRAiDyuAgBN6XpQ"]["indices"]
    print(node["query_cache"]["memory_size_in_bytes"])
    print(node["request_cache"]["memory_size_in_bytes"])
    return node["query_cache"]["memory_size_in_bytes"] / 1000, node["request_cache"]["memory_size_in_bytes"] / 1000


##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME_A = "location-index"
    COUNTRY_FILE = "./keyword.csv"
    SIZE = 300
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))
    client.indices.clear_cache()
    run_query_loop()
    print("Done.")
