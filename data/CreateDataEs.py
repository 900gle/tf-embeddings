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
            "_source": ["name", "keyword", "category", "price"]
        }
    )

    # es_data = []
    f = open(FILE_NAME, 'w', encoding='utf-8')

    for hit in response["hits"]["hits"]:
        if (len(hit["_source"]["name"]) > 1):
            row = dict(name=str(hit["_source"]["name"]), keyword=str(hit["_source"]["keyword"]),
                       category=str(hit["_source"]["category"]), price=str(hit["_source"]["price"]),
                       rank=randint(1, 1000))
            f.write(json.dumps(row, ensure_ascii=False))
            f.write("\n")
    f.close()


if __name__ == '__main__':
    INDEX_NAME = "goods"
    FILE_NAME = "products/goods.json"
    SEARCH_SIZE = 10000
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    create()

    print("Done.")
