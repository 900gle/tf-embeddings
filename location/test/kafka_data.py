# -*- coding: utf-8 -*-

import json
import csv

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import tensorflow_hub as hub
import tensorflow_text
import kss, numpy
from random import *
import traceback
from kafka import KafkaProducer


def is_number(x):
    try:
        # only integers and float converts safely
        num = float(x)
        return True
    except ValueError as e: # not convertable to float
        return False

##### INDEXING #####
def index_data():


    csv_mapping_list = []
    with open(DATA_FILE) as my_data:
        csv_reader = csv.reader(my_data, delimiter=",")
        line_count = 0

        for line in csv_reader:
            if line_count == 0:
                header = line
            else:
                row_dict = {'private_ip': line[0], 'public_ip': line[1], 'country_code': line[2], 'city': line[3],
                            'addr1': line[4], 'location': {'lat':line[5], 'lon': line[6]}, 'no': line[7], 'country': line[8], 'num': randint(1, 10000) }

                if is_number(line[5]) and is_number(line[6]):
                    producer(row_dict)
            line_count += 1

def producer(messege):
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        client_id='5amsung',
        key_serializer=None,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    try:
        response = producer.send(topic='5amsung', value=messege).get()
    except:
        traceback.print_exc()

    print(response)


##### MAIN SCRIPT #####
if __name__ == '__main__':
    INDEX_NAME_A = "location-index"
    INDEX_FILE_A = "./data/location/index.json"
    DATA_FILE = "./data/dbip-location-2016-01.csv"
    BATCH_SIZE = 5000
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))
    index_data()

    print("Done.")
