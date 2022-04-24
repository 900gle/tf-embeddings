# -*- coding: utf-8 -*-

import time

from elasticsearch import Elasticsearch

import tensorflow_hub as hub
import tensorflow_text


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
    query_vector = embed_text([query])[0]
    embedding_time = time.time() - embedding_start

    script_query = {
        "function_score": {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^5",
                        "category"
                    ]
                }
            },
            "functions": [
                {
                    "script_score": {
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'feature_vector') * doc['weight'].value * doc['populr'].value / doc['name'].length + doc['category'].length",
                            "params": {
                                "query_vector": query_vector
                            }
                        }
                    },
                    "weight": 1
                }
            ]
        }
    }

    search_start = time.time()
    response = client.search(
        index=INDEX_NAME,
        body={
            "size": SEARCH_SIZE,
            "query": script_query,
            "_source": {"includes": ["name", "category", "price"]},
            "sort" : [
                {
                    "_script": {
                        "type": "number",
                        "order": "desc",
                        "script": {
                            "source": "doc['price'].value / params.searchKeyword",
                            "params": {
                                "searchKeyword": 10000
                            }
                        }
                    }
                },
                {"price" : {"order" : "asc"}}
            ]
        }
    )
    
    search_time = time.time() - search_start

    print()
    print("{} total hits.".format(response["hits"]["total"]["value"]))
    print("embedding time: {:.2f} ms".format(embedding_time * 1000))
    print("search time: {:.2f} ms".format(search_time * 1000))
    for hit in response["hits"]["hits"]:
        print("id: {}, score: {}".format(hit["_id"], hit["_score"]))
        print(hit["_source"])
        print()


##### EMBEDDING #####

def embed_text(input):
    vectors = model(input)
    return [vector.numpy().tolist() for vector in vectors]


##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME = "goods"

    SEARCH_SIZE = 3
    print("Downloading pre-trained embeddings from tensorflow hub...")
    model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    run_query_loop()

    print("Done.")