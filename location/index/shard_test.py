# -*- coding: utf-8 -*-
import time
import json
import csv

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import matplotlib.pyplot as plt
import kss, numpy


def is_number(x):
    try:
        # only integers and float converts safely
        num = float(x)
        return True
    except ValueError as e:  # not convertable to float
        return False


##### INDEXING #####
def index_create(shard_size):
    INDEX = INDEX_NAME + shard_size
    indexs.append(INDEX)
    print("Creating the '" + INDEX + "' index.")
    client.indices.delete(index=INDEX, ignore=[404])

    with open(INDEX_FILE_A) as index_file:
        source = index_file.read().strip().replace('SHARD_SIZE', shard_size)
        client.indices.create(index=INDEX, body=source)


def index_data(INDEX):
    csv_mapping_list = []
    bulk_times = []
    with open(DATA_FILE) as my_data:
        csv_reader = csv.reader(my_data, delimiter=",")
        line_count = 0

        for line in csv_reader:
            if line_count == 0:
                header = line
            else:
                row_dict = {'private_ip': line[0], 'public_ip': line[1], 'country_code': line[2], 'city': line[3],
                            'addr1': line[4], 'location': {'lat':line[5], 'lon': line[6]}, 'no': line[7], 'country': line[8]}

                if is_number(line[5]) and is_number(line[6]):
                    csv_mapping_list.append(row_dict)
            line_count += 1

            if line_count % BATCH_SIZE == 0:
                bulk_times.append(index_batch_a(INDEX, csv_mapping_list))
                csv_mapping_list = []

                # print("Indexed {} documents.".format(line_count))
        if csv_mapping_list:
            bulk_times.append(index_batch_a(INDEX, csv_mapping_list))
            # print("Indexed {} documents.".format(line_count))

    return bulk_times

def refresh_index(INDEX):
    client.indices.refresh(index=INDEX)
    print("Done indexing.")


def index_batch_a(INDEX, docs):
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX
        requests.append(request)

    bulk_start = time.time()
    bulk(client, requests, pipeline='timestamp')
    return ( time.time() - bulk_start)

##### MAIN SCRIPT #####
if __name__ == '__main__':
    INDEX_NAME = "shard-"
    SHARD_SIZE_A = '1'
    INDEX_FILE_A = "./data/location/shard_index.json"
    DATA_FILE = "./data/dbip-location-2016-01.csv"
    # DATA_FILE = "./data/test.csv"
    BATCH_SIZE = 5000
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))
    indexs = []
    times = []
    bulk_time_array = []

    for i in range(1, 10):
        index_create(str(i))

    for index in indexs :
        search_start = time.time()
        bulk_time_array.append(index_data(index))
        times.append( time.time() - search_start)

    t= range(0, len(times))

    plt.rcParams['font.family'] = 'AppleGothic'

    fig, ax = plt.subplots()
    ax.set_title('shard 와 index')

    lines = []
    i = 1;
    for bta in bulk_time_array:
        t= range(0, len(bta))
        lines.append(ax.plot(t, bta, lw=2, label='shards'+str(i)))
        i=i+1
    leg = ax.legend(fancybox=True, shadow=True)

    ax.set_ylabel('time')
    ax.set_xlabel('shard')

    lined = {}  # Will map legend lines to original lines.
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(True)  # Enable picking on the legend line.
        lined[legline] = origline

    def on_pick(event):
        legline = event.artist
        origline = lined[legline]
        visible = not origline.get_visible()
        origline.set_visible(visible)
        legline.set_alpha(1.0 if visible else 0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', on_pick)
    plt.show()

    for index in indexs :
        refresh_index(index)

    print("Done.")
