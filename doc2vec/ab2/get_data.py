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
    query_vector_a = embed_text_a([query])[0]
    query_vector_b = embed_text_b([query])[0]
    embedding_time = time.time() - embedding_start

    script_query_a = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['name_vector']) + 1.0",
                "params": {"query_vector": query_vector_a}
            }
        }
    }

    script_query_b = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['name_vector']) + 1.0",
                "params": {"query_vector": query_vector_b}
            }
        }
    }

    search_start = time.time()
    response_a = client.search(
        index=INDEX_NAME_A,
        body={
            "size": SEARCH_SIZE,
            "query": script_query_a,
            "_source": {"includes": ["name", "category"]}
        }
    )

    response_b = client.search(
        index=INDEX_NAME_B,
        body={
            "size": SEARCH_SIZE,
            "query": script_query_b,
            "_source": {"includes": ["name", "category"]}
        }
    )
    search_time = time.time() - search_start


    print("검색어 :" , query)
    print()
    print("CASE A : ")
    for hit in response_a["hits"]["hits"]:
        print("name: {}, category: {}, score: {}".format(hit["_source"]["name"], hit["_source"]["category"], hit["_score"]))
    print()
    print("CASE B : ")
    for hit in response_b["hits"]["hits"]:
        print("name: {}, category: {}, score: {}".format(hit["_source"]["name"], hit["_source"]["category"], hit["_score"]))

##### EMBEDDING #####

def embed_text_a(input):
    vectors = embed_a(input)
    return [vector.numpy().tolist() for vector in vectors]

def embed_text_b(input):
    vectors = embed_b(input)
    return [vector.numpy().tolist() for vector in vectors]

##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME_A = "products_a2"
    INDEX_NAME_B = "products_b2"
    INDEX_FILE = "./data/products/index.json"

    DATA_FILE = "./data/products/products.json"
    BATCH_SIZE = 100

    SEARCH_SIZE = 3

    print("Downloading pre-trained embeddings from tensorflow hub...")
    embed_a = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")
    embed_b = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")

    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    run_query_loop()
    print("Done.")
