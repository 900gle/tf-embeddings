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

##### INDEXING #####

def index_data():
    print("Creating the '" + INDEX_NAME_A + "' index.")
    print("Creating the '" + INDEX_NAME_B + "' index.")
    client.indices.delete(index=INDEX_NAME_A, ignore=[404])
    client.indices.delete(index=INDEX_NAME_A, ignore=[404])

    with open(INDEX_FILE) as index_file:
        source = index_file.read().strip()
        client.indices.create(index=INDEX_NAME_A, body=source)
        client.indices.create(index=INDEX_NAME_B, body=source)

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
                index_batch_b(docs)
                docs = []
                print("Indexed {} documents.".format(count))

        if docs:
            index_batch_a(docs)
            index_batch_b(docs)
            print("Indexed {} documents.".format(count))

    client.indices.refresh(index=INDEX_NAME_A)
    client.indices.refresh(index=INDEX_NAME_B)
    print("Done indexing.")


def paragraph_index(paragraph):
    # 문장단위 분리
    avg_paragraph_vec = numpy.zeros((1, 512))
    sent_count = 0
    for sent in kss.split_sentences(paragraph[0:100]):
        # 문장을 embed 하기
        # vector들을 평균으로 더해주기
        avg_paragraph_vec += embed_text([sent])
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

def index_batch_b(docs):
    name = [doc["name"] for doc in docs]
    name_vectors = embed_text_b(name)
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME_B
        request["name_vector"] = name_vectors[i]
        requests.append(request)
    bulk(client, requests)
##### EMBEDDING #####

def embed_text_a(input):
    vectors = embed_a(input)
    return [vector.numpy().tolist() for vector in vectors]

def embed_text_b(input):
    vectors = embed_b(input)
    return [vector.numpy().tolist() for vector in vectors]

##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME_A = "products_a"
    INDEX_NAME_B = "products_b"
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
