# -*- coding: utf-8 -*-
import random
import time
import json
import csv

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import matplotlib.pyplot as plt
import kss, numpy

##### INDEXING #####
def index_create(INDEX, INDEX_FILE):
    print("Creating the '" + INDEX + "' index.")
    client.indices.delete(index=INDEX, ignore=[404])

    with open(INDEX_FILE) as index_file:
        source = index_file.read().strip().replace('{SHARD_SIZE}', SHARD_SIZE)
        client.indices.create(index=INDEX, body=source)
def indexing():
    datas = []
    line_count = 0
    for i in range(0, DATA_LOWS):
        promos = []
        name = "상품-" + str(i)
        for j in range(0, random.randint(1,50)):
            promo = random.randint(1000, 2000)
            print(promo)
            theme = []
            for k in range (0,random.randint(1,6)):
                theme.append(random.randint(10000, 20000))
            promos.append({'promo': promo, 'theme': theme})
        line_count += 1
        row_dict = {'name': name, 'promos': promos}
        datas.append(row_dict)

        if line_count % BATCH_SIZE == 0:
            index_batch(NESTED_INDEX, datas)
            index_batch(OBJECT_INDEX, datas)
            datas = []

    if len (datas) > 0:
        index_batch(NESTED_INDEX, datas)
        index_batch(OBJECT_INDEX, datas)
        datas = []

    refresh_index(NESTED_INDEX)
    refresh_index(OBJECT_INDEX)

def refresh_index(INDEX):
    client.indices.refresh(index=INDEX)
    print("Done indexing.")

def index_batch(INDEX, docs):
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX
        requests.append(request)

    bulk_start = time.time()
    bulk(client, requests, pipeline='timestamp')
    return (time.time() - bulk_start)

##### MAIN SCRIPT #####
if __name__ == '__main__':
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    INDEX_NAME = "aggs-"
    SHARD_SIZE = '1'
    NESTED_INDEX = INDEX_NAME + "nasted-index"
    NESTED_INDEX_FILE = "../sql/nested_aggs_index.json"

    OBJECT_INDEX = INDEX_NAME + "object-index"
    OBJECT_INDEX_FILE = "../sql/object_aggs_index.json"

    DATA_LOWS = 10000000
    BATCH_SIZE = 5000

    index_create(NESTED_INDEX, NESTED_INDEX_FILE)
    index_create(OBJECT_INDEX, OBJECT_INDEX_FILE)

    indexing()
    print("Done.")
