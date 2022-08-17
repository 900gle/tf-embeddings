# -*- coding: utf-8 -*-
import json
from random import *

from elasticsearch import Elasticsearch


def create():
    script_query = {
        "match_all": {}
    }

    response = client.search(
        index=INDEX_NAME,
        body={
            "size": SEARCH_SIZE,
            "query": script_query,
            "_source": ["name", "keyword"]
        }
    )

    es_data = []

    for hit in response["hits"]["hits"]:
        row = dict(name=str(hit["_source"]["name"]), keyword=str(hit["_source"]["keyword"]), rank=randint(1, 1000))
        es_data.append(row)

    f = open(FILE_NAME, 'w', encoding='utf-8')
    f.write(json.dumps(es_data, ensure_ascii=False))
    f.close()


if __name__ == '__main__':
    INDEX_NAME = "goods"
    FILE_NAME = "similarity_data.json"
    SEARCH_SIZE = 9000
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    create()

    print("Done.")
