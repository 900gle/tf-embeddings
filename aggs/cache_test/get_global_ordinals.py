# -*- coding: utf-8 -*-
import time

import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
import numpy as np


##### SEARCHING #####

def run_query_loop():
    time_a = []
    time_b = []

    for i in range(SIZE):
        time_a.append(query_a())
        time_b.append(query_b())

    print("AGGS 평균 : " + str(round(np.mean(time_a), 2)))
    print("AGGS ORDINALS 평균 : " + str(round(np.mean(time_b), 2)))

    t = range(0, SIZE)
    plt.rcParams['font.family'] = 'AppleGothic'

    fig, ax = plt.subplots()
    ax.set_title('AGGS vs AGGS ORDINALS')
    line1, = ax.plot(t, time_a, lw=2, label='AGGS')
    line2, = ax.plot(t, time_b, lw=2, label='AGGS ORDINALS')
    leg = ax.legend(fancybox=True, shadow=True)

    ax.set_ylabel('score')
    ax.set_xlabel('top' + str(SIZE))

    lines = [line1, line2]
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


def query_a():
    with open(AGGS_A) as index_file:
        script_query = index_file.read().strip()
    search_start = time.time()
    client.search(
        index=INDEX_NAME_A,
        body=script_query
    )

    search_time = time.time() - search_start
    return search_time * 1000


def query_b():
    with open(AGGS_B) as index_file:
        script_query = index_file.read().strip()
    search_start = time.time()
    client.search(
        index=INDEX_NAME_A,
        body=script_query
    )

    search_time = time.time() - search_start
    return search_time * 1000


##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME_A = "aggs-ordinals-index"
    AGGS_A = "./query/aggs_query.json"
    AGGS_B = "./query/aggs_ordinals_query.json"
    SIZE = 50
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))
    run_query_loop()
    print("Done.")

