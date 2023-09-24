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
    print("Creating the '" + INDEX_NAME_C + "' index.")
    client.indices.delete(index=INDEX_NAME_A, ignore=[404])
    client.indices.delete(index=INDEX_NAME_B, ignore=[404])
    client.indices.delete(index=INDEX_NAME_C, ignore=[404])

    with open(INDEX_FILE_A) as index_file:
        source = index_file.read().strip()
        client.indices.create(index=INDEX_NAME_A, body=source)

    with open(INDEX_FILE_B) as index_file:
        source = index_file.read().strip()
        client.indices.create(index=INDEX_NAME_B, body=source)

    with open(INDEX_FILE_C) as index_file:
        source = index_file.read().strip()
        client.indices.create(index=INDEX_NAME_C, body=source)
    count = 0
    docs = []

    with open(DATA_FILE, 'r') as data_file:
        json_object = json.loads(data_file.read())
        for line in json_object:
            docs.append(line)
            count += 1

            if count % BATCH_SIZE == 0:
                index_batch_a(docs)
                index_batch_b(docs)
                index_batch_c(docs)
                docs = []
                print("Indexed {} documents.".format(count))

        if docs:
            index_batch_a(docs)
            index_batch_b(docs)
            index_batch_c(docs)
            print("Indexed {} documents.".format(count))

    client.indices.refresh(index=INDEX_NAME_A)
    client.indices.refresh(index=INDEX_NAME_B)
    client.indices.refresh(index=INDEX_NAME_C)
    print("Done indexing.")

def index_batch_a(docs):
    name = [doc["name"] for doc in docs]
    category = [doc["name"] for doc in docs]
    name_vectors = embed_text(name)
    category_vectors = embed_text(category)
    feature_vectors = embed_text(name + category)
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME_A
        request["name_vector"] = name_vectors[i]
        request["category_vector"] = category_vectors[i]
        request["feature_vector"] = feature_vectors[i]
        requests.append(request)
    bulk(client, requests)

def index_batch_b(docs):
    name = [doc["name"] for doc in docs]
    category = [doc["name"] for doc in docs]
    name_vectors = embed_text(name)
    category_vectors = embed_text(category)
    feature_vectors = embed_text(name + category)
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME_B
        request["name_vector"] = name_vectors[i]
        request["category_vector"] = category_vectors[i]
        request["feature_vector"] = feature_vectors[i]
        requests.append(request)
    bulk(client, requests)

def index_batch_c(docs):
    name = [doc["name"] for doc in docs]
    category = [doc["name"] for doc in docs]
    name_vectors = embed_text(name)
    category_vectors = embed_text(category)
    feature_vectors = embed_text(name + category)
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME_C
        request["name_vector"] = name_vectors[i]
        request["category_vector"] = category_vectors[i]
        request["feature_vector"] = feature_vectors[i]
        requests.append(request)
    bulk(client, requests)

def paragraph_index(paragraph):
    # 문장단위 분리
    avg_paragraph_vec = numpy.zeros((1, 128))
    sent_count = 0
    for sent in kss.split_sentences(paragraph[0:100]):
        # 문장을 embed 하기
        # vector들을 평균으로 더해주기
        avg_paragraph_vec += embed_text([sent])
        sent_count += 1
    avg_paragraph_vec /= sent_count
    return avg_paragraph_vec.ravel(order='C')

##### EMBEDDING #####
def embed_text(input):
    vectors = embed(input)
    return [vector.numpy().tolist() for vector in vectors]

##### MAIN SCRIPT #####
if __name__ == '__main__':
    INDEX_NAME_A = "ann-index"
    INDEX_FILE_A = "./data/products/ann-index.json"

    INDEX_NAME_B = "knn-index"
    INDEX_FILE_B = "./data/products/knn-index.json"

    INDEX_NAME_C = "match-index"
    INDEX_FILE_C = "./data/products/knn-index.json"

    DATA_FILE = "./db/json_data.json"
    BATCH_SIZE = 100
    SEARCH_SIZE = 3

    print("Downloading pre-trained embeddings from tensorflow hub...")
    embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")

    client = Elasticsearch(http_auth=('elastic', 'dlengus'))
    index_data()

    print("Done.")