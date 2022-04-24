# -*- coding: utf-8 -*-

import time

from elasticsearch import Elasticsearch

import tensorflow_hub as hub
import tensorflow_text


##### SEARCHING #####


def handle_query():
    # query = input("Enter query: ")
    query = "나이키 남성 후드티"

    embedding_start = time.time()
    query_vector = embed_text([query])[0]
    embedding_time = time.time() - embedding_start

    script_query = {
        "function_score": {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "name",
                                    "category"
                                ]
                            }
                        }],
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "category1",
                                    "category2",
                                    "category3",
                                    "category4",
                                    "category5"
                                ]
                            }
                        }
                    ]
                }
            },
            "boost_mode": "multiply",
            "functions": [
                {
                    "script_score": {
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'feature_vector') * doc['weight'].value * doc['popular'].value / doc['name.keyword'].length + doc['category.keyword'].length",
                            "params": {
                                "query_vector": query_vector
                            }
                        }
                    },
                    "weight": 0.1
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
            "_source": {"includes": ["name", "category"]}
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

    SEARCH_SIZE = 10
    print("Downloading pre-trained embeddings from tensorflow hub...")
    model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    handle_query()

    print("Done.")