# -*- coding: utf-8 -*-

import csv

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


##### INDEXING #####
def index_data():
    print("Creating the '" + INDEX_NAME_A + "' index.")
    client.indices.delete(index=INDEX_NAME_A, ignore=[404])

    with open(INDEX_FILE_A) as index_file:
        source = index_file.read().strip()
        client.indices.create(index=INDEX_NAME_A, body=source)

    csv_mapping_list = []
    with open(DATA_FILE) as my_data:
        csv_reader = csv.reader(my_data, delimiter=",")
        line_count = 0
        for line in csv_reader:
            if line_count == 0:
                header = line
            else:
                row_dict = {'country_code': line[2], 'country_code_ordinals': line[2]}
                csv_mapping_list.append(row_dict)
            line_count += 1
            if line_count % BATCH_SIZE == 0:
                index_batch_a(csv_mapping_list)
                csv_mapping_list = []

                print("Indexed {} documents.".format(line_count))
        if csv_mapping_list:
            index_batch_a(csv_mapping_list)
            print("Indexed {} documents.".format(line_count))

    client.indices.refresh(index=INDEX_NAME_A)
    print("Done indexing.")

def index_batch_a(docs):
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME_A
        requests.append(request)
    bulk(client, requests, pipeline='timestamp')

##### MAIN SCRIPT #####
if __name__ == '__main__':
    INDEX_NAME_A = "aggs-ordinals-index"
    INDEX_FILE_A = "../../data/location/aggs_index.json"
    DATA_FILE = "../../data/dbip-location-2016-01.csv"
    BATCH_SIZE = 5000
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))
    index_data()

    print("Done.")
