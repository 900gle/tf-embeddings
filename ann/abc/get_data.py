# -*- coding: utf-8 -*-
import time
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import tensorflow_hub as hub
import tensorflow_text
import matplotlib.pyplot as plt
import kss, numpy

##### SEARCHING #####

def run_query_loop():
    while True:
        try:
            handle_query()
        except KeyboardInterrupt:
            return

def handle_query():
    query = input("Enter query: ")

    embedding_start = time.time()
    query_vector = embed_text([query])[0]
    embedding_time = time.time() - embedding_start

    with open(ANN) as index_file:
        script_query_a = index_file.read().strip()
        script_query_a = script_query_a.replace("{query_vector}", str(query_vector))
        script_query_a = script_query_a.replace("{SEARCH_SIZE}", str(SEARCH_SIZE))

    with open(KNN) as index_file:
        script_query_b = index_file.read().strip()
        script_query_b = script_query_b.replace("{query_vector}", str(query_vector))
        script_query_b = script_query_b.replace("{SEARCH_SIZE}", str(SEARCH_SIZE))

    with open(MATCH) as index_file:
        script_query_c = index_file.read().strip()
        script_query_c = script_query_c.replace("{query}", str(query))
        script_query_c = script_query_c.replace("{SEARCH_SIZE}", str(SEARCH_SIZE))

    search_start = time.time()
    response_a = client.search(
        index=INDEX_NAME_A,
        body=script_query_a
    )
    response_b = client.search(
        index=INDEX_NAME_B,
        body=script_query_b
    )

    print(script_query_c)
    response_c = client.search(
        index=INDEX_NAME_C,
        body=script_query_c
    )

    search_time = time.time() - search_start
    score_a =[]
    score_b =[]
    score_c =[]

    print("검색어 :", query)
    print("CASE A : ")
    for hit in response_a["hits"]["hits"]:
        score_a.append(hit["_score"])
        print("name: {}, category: {}, score: {}".format(hit["_source"]["name"], hit["_source"]["category"], hit["_score"]))

    print("CASE B : ")
    for hit in response_b["hits"]["hits"]:
        score_b.append(hit["_score"])
        print("name: {}, category: {}, score: {}".format(hit["_source"]["name"], hit["_source"]["category"], hit["_score"]))

    print("CASE C : ")
    for hit in response_c["hits"]["hits"]:
        score_c.append(hit["_score"])
        print("name: {}, category: {}, score: {}".format(hit["_source"]["name"], hit["_source"]["category"], hit["_score"]))

    t= range(0, SEARCH_SIZE)
    plt.rcParams['font.family'] = 'AppleGothic'

    fig, ax = plt.subplots()
    ax.set_title('ANN vs kNN vs match')
    line1, = ax.plot(t, score_a, lw=2, label='ANN')
    line2, = ax.plot(t, score_b, lw=2, label='kNN')
    line3, = ax.plot(t, score_c, lw=2, label='match')
    leg = ax.legend(fancybox=True, shadow=True)

    ax.set_ylabel('score')
    ax.set_xlabel('top' + str(SEARCH_SIZE))

    lines = [line1, line2, line3]
    lined = {}  # Will map legend lines to original lines.
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




##### EMBEDDING #####

def embed_text(input):
    vectors = embed(input)
    return [vector.numpy().tolist() for vector in vectors]

##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME_A = "ann-index"
    INDEX_NAME_B = "knn-index"
    INDEX_NAME_C = "match-index"

    ANN = "ann/query/ann_query.json"
    KNN = "ann/query/knn_query.json"
    MATCH = "ann/query/match_query.json"

    SEARCH_SIZE = 10

    print("Downloading pre-trained embeddings from tensorflow hub...")
    embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))
    run_query_loop()
    print("Done.")
