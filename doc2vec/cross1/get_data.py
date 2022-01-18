# -*- coding: utf-8 -*-
import time

import tensorflow_hub as hub
from elasticsearch import Elasticsearch


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

    search_start = time.time()
    response_a = client.search(
        index=INDEX_NAME_A,
        body={
            "size": SEARCH_SIZE,
            "query": query(query,query_vector),
            "_source": {"includes": ["name", "category"]}
        }
    )

    response_b = client.search(
        index=INDEX_NAME_B,
        body={
            "size": SEARCH_SIZE,
            "query": query(query,query_vector),
            "_source": {"includes": ["name", "category"]}
        }
    )
    search_time = time.time() - search_start

    print()
    print("검색어 :" , query)
    print("CASE A : ")
    for hit in response_a["hits"]["hits"]:
        print("name: {}, category: {}, score: {}".format(hit["_source"]["name"], hit["_source"]["category"], hit["_score"]))
    print()
    print("CASE B : ")
    for hit in response_b["hits"]["hits"]:
        print("name: {}, category: {}, score: {}".format(hit["_source"]["name"], hit["_source"]["category"], hit["_score"]))

##### QUERY #####
def query(query, vector):
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['name_vector']) + 1.0",
                "params": {"query_vector": vector}
            }
        }
    }
    return script_query

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
