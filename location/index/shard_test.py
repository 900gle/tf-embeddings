# -*- coding: utf-8 -*-

import json
import csv

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import tensorflow_hub as hub
import tensorflow_text
import kss, numpy


def is_number(x):
    try:
        # only integers and float converts safely
        num = float(x)
        return True
    except ValueError as e:  # not convertable to float
        return False


##### INDEXING #####
def index_data(shard_size):
    INDEX = INDEX_NAME + shard_size
    print("Creating the '" + INDEX + "' index.")
    client.indices.delete(index=INDEX, ignore=[404])

    with open(INDEX_FILE_A) as index_file:
        source = index_file.read().strip().replace('SHARD_SIZE', shard_size)
        client.indices.create(index=INDEX, body=source)
    csv_mapping_list = []
    # with open(DATA_FILE) as my_data:
    #     csv_reader = csv.reader(my_data, delimiter=",")
    #     line_count = 0
    #
    #     for line in csv_reader:
    #         if line_count == 0:
    #             header = line
    #         else:
    #             row_dict = {'private_ip': line[0], 'public_ip': line[1], 'country_code': line[2], 'city': line[3],
    #                         'addr1': line[4], 'location': {'lat':line[5], 'lon': line[6]}, 'no': line[7], 'country': line[8]}
    #
    #             if is_number(line[5]) and is_number(line[6]):
    #                 csv_mapping_list.append(row_dict)
    #         line_count += 1
    #
    #         if line_count % BATCH_SIZE == 0:
    #             index_batch_a(csv_mapping_list)
    #             csv_mapping_list = []
    #
    #             print("Indexed {} documents.".format(line_count))
    #     if csv_mapping_list:
    #         index_batch_a(INDEX ,csv_mapping_list)
    #         print("Indexed {} documents.".format(line_count))
    #
    # client.indices.refresh(index=INDEX_NAME_A)
    print("Done indexing.")


def index_batch_a(INDEX, docs):
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX
        requests.append(request)
    bulk(client, requests, pipeline='timestamp')


##### MAIN SCRIPT #####
if __name__ == '__main__':
    INDEX_NAME = "shard-"
    SHARD_SIZE_A = '1'
    INDEX_FILE_A = "./data/location/shard_index.json"
    DATA_FILE = "./data/dbip-location-2016-01.csv"
    BATCH_SIZE = 5000
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))
    for i in range(1, 10):
        index_data(str(i))

    print("Done.")
