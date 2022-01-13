# -*- coding: utf-8 -*-
import time
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import tensorflow_hub as hub
import tensorflow_text
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

    script_query_a = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['name_vector']) + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }

    script_query_b = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['name_vector']) + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }

    search_start = time.time()
    response_a = client.search(
        index=INDEX_NAME_A,
        body={
            "size": SEARCH_SIZE,
            "query": script_query_a,
            "_source": {"includes": ["name", "price"]}
        }
    )

    response_b = client.search(
        index=INDEX_NAME_B,
        body={
            "size": SEARCH_SIZE,
            "query": script_query_b,
            "_source": {"includes": ["name", "price"]}
        }
    )
    search_time = time.time() - search_start


    print("검색어 :" , query)
    print()
    print("CASE A : ")
    for hit in response_a["hits"]["hits"]:
        print("id: {}, score: {}".format(hit["_id"], hit["_score"]))
        print(hit["_source"]["name"])
        print()
    print()
    print("CASE B : ")
    for hit in response_b["hits"]["hits"]:
        print("id: {}, score: {}".format(hit["_id"], hit["_score"]))
        print(hit["_source"]["name"])
        print()

##### EMBEDDING #####

def embed_text(input):
    vectors = embed(input)
    return [vector.numpy().tolist() for vector in vectors]

##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME_A = "products_a"
    INDEX_NAME_B = "products_a2"
    INDEX_FILE = "./data/products/index.json"

    DATA_FILE = "./data/products/products.json"
    BATCH_SIZE = 100

    SEARCH_SIZE = 3

    print("Downloading pre-trained embeddings from tensorflow hub...")
    embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")

    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    run_query_loop()
    print("Done.")
