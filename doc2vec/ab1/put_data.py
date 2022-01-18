# -*- coding: utf-8 -*-

import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import tensorflow_hub as hub
import tensorflow_text
import kss, numpy


##### INDEXING #####

def index_data():
    print("Creating the '" + INDEX_NAME_A + "' index.")
    print("Creating the '" + INDEX_NAME_B + "' index.")
    client.indices.delete(index=INDEX_NAME_A, ignore=[404])
    client.indices.delete(index=INDEX_NAME_B, ignore=[404])

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

    index_data()

    print("Done.")