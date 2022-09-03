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
    embedding_time = time.time() - embedding_start

    script_query_a = {
            "query": {
                "match": {
                    "name": {
                        "query": query,
                        "boost": 0.9
                    }
                }
            },
            "knn": {
                "field": "name_vector",
                "query_vector": query_vector_a,
                "k": 5,
                "num_candidates": 50,
                "boost": 0.1
            },
            "size": 10
        }

    search_start = time.time()
    response_a = client.search(
        index=INDEX_NAME_A,
        body= script_query_a
    )


    search_time = time.time() - search_start

    print("검색어 :" , query)
    print()
    print("CASE A : ")
    for hit in response_a["hits"]["hits"]:
        print("name: {}, category: {}, score: {}".format(hit["_source"]["name"], hit["_source"]["category"], hit["_score"]))


##### INDEXING #####

def index_data():
    print("Creating the '" + INDEX_NAME_A + "' index.")
    client.indices.delete(index=INDEX_NAME_A, ignore=[404])

    with open(INDEX_FILE) as index_file:
        source = index_file.read().strip()
        client.indices.create(index=INDEX_NAME_A, body=source)

    count = 0
    docs = []

    with open(DATA_FILE) as data_file:
        for line in data_file:
            line = line.strip()

            json_data = json.loads(line)

            docs.append(json_data)
            count += 1

            if count % BATCH_SIZE == 0:
                index_batch_a(docs)
                docs = []
                print("Indexed {} documents.".format(count))

        if docs:
            index_batch_a(docs)
            print("Indexed {} documents.".format(count))

    client.indices.refresh(index=INDEX_NAME_A)
    print("Done indexing.")


def paragraph_index(paragraph):
    # 문장단위 분리
    avg_paragraph_vec = numpy.zeros((1, 512))
    sent_count = 0
    for sent in kss.split_sentences(paragraph[0:100]):
        # 문장을 embed 하기
        # vector들을 평균으로 더해주기
        avg_paragraph_vec += embed_a([sent])
        sent_count += 1
    avg_paragraph_vec /= sent_count
    return avg_paragraph_vec.ravel(order='C')


def index_batch_a(docs):
    name = [doc["name"] for doc in docs]
    name_vectors = embed_text_a(name)
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME_A
        request["name_vector"] = name_vectors[i]
        requests.append(request)
    bulk(client, requests)


##### EMBEDDING #####

def embed_text_a(input):
    vectors = embed_a(input)
    return [vector.numpy().tolist() for vector in vectors]



##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME_A = "ann-test"
    INDEX_FILE = "./data/products/ann-index.json"
    DATA_FILE = "./data/products/products.json"
    BATCH_SIZE = 100

    SEARCH_SIZE = 3

    print("Downloading pre-trained embeddings from tensorflow hub...")
    embed_a = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")

    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    run_query_loop()
    print("Done.")
