# -*- coding: utf-8 -*-
import time

import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
import numpy as np


##### SEARCHING #####

def run_query_loop():
    time_a = []
    query_c = []
    request_c = []

    with open(PROMO_FILE) as data_file:
        for line in data_file:
            line = line.strip()
            time_a.append(query_nested(line))
            # time_a.append(query_object(line))
            query_cache, request_cache = cache_monitoring()
            query_c.append(query_cache)
            request_c.append(request_cache)

    print("AGGS 평균 : " + str(round(np.mean(time_a), 2)))

    t = range(0, len(time_a))
    plt.rcParams['font.family'] = 'AppleGothic'

    fig, ax = plt.subplots()
    ax.set_title('AGGS cache')
    line1, = ax.plot(t, time_a, lw=1, label='Aggs')
    line2, = ax.plot(t, query_c, lw=1, label='Query c')
    line3, = ax.plot(t, request_c, lw=1, label='Request c')
    leg = ax.legend(fancybox=True, shadow=True)

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


def query_nested(keyword):
    with open(AGGS_NESTED) as index_file:
        script_query = index_file.read().strip()
        script_query = script_query.replace("{promo_no}", str(keyword))

    search_start = time.time()
    response = client.search(
        index=NESTED_INDEX,
        body=script_query
    )
    search_time = time.time() - search_start
    return search_time * 1000


def query_object(keyword):
    with open(AGGS_OBJECT) as index_file:
        script_query = index_file.read().strip()
        script_query = script_query.replace("{promo_no}", str(keyword))

    search_start = time.time()
    response = client.search(
        index=OBJECT_INDEX,
        body=script_query
    )
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
    NESTED_INDEX = "aggs-nasted-index"
    OBJECT_INDEX = "aggs-object-index"

    AGGS_NESTED = "../query/nested_query.json"
    AGGS_OBJECT = "../query/object_query.json"

    PROMO_FILE = "./data/promo.txt"

    SIZE = 300
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))
    client.indices.clear_cache()
    run_query_loop()
    print("Done.")
