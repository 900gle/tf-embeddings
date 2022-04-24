# -*- coding: utf-8 -*-

import time
import math

from elasticsearch import Elasticsearch

import tensorflow_hub as hub
import tensorflow_text

import matplotlib.pyplot as plt
import numpy as np

##### SEARCHING #####

def get_result(script_query):
    response = client.search(
        index=INDEX_NAME,
        body={
            "size": SEARCH_SIZE,
            "query": script_query,
            "_source": {"includes": ["name", "category"]}
        }
    )

    return [hit["_score"] for hit in response["hits"]["hits"]]

def handle_query():
    query = "나이키 남성 신발"
    query_vector = embed_text([query])[0]

    script_query1 = {
        "function_score": {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name",
                        "category^2"
                    ]
                }
            },
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

    script_query2 = {
        "function_score": {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name",
                        "category"
                    ]
                }
            },
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


    script_query3 = {
        "function_score": {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^2",
                        "category"
                    ]
                }
            },
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

    # print(response["hits"]["max_score"])
    x = np.arange(0, SEARCH_SIZE, 1)
    y1 = get_result(script_query1)
    y2 = get_result(script_query2)
    y3 = get_result(script_query3)

    plt.xlim([1, SEARCH_SIZE])      # X축의 범위: [xmin, xmax]
    plt.ylim([0, MAX_SCORE])     # Y축의 범위: [ymin, ymax]
    plt.xlabel('top 10', labelpad=2)
    plt.ylabel('score', labelpad=2)
    plt.plot(x, y1, label='query1', color='#e35f62', marker='*', linewidth=1 )
    plt.plot(x, y2, label='query2', color='#008000', marker='*', linewidth=1 )
    plt.plot(x, y3, label='query3', color='#3333cc', marker='*', linewidth=1 )

    plt.legend()
    plt.title('Query score')
    plt.xticks(x)
    plt.yticks(np.arange(1, MAX_SCORE))
    plt.grid(True)
    plt.show()

##### EMBEDDING #####

def embed_text(input):
    vectors = model(input)
    return [vector.numpy().tolist() for vector in vectors]


##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME = "goods"

    SEARCH_SIZE = 10
    MAX_SCORE = 3
    print("Downloading pre-trained embeddings from tensorflow hub...")
    model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")
    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    handle_query()

    print("Done.")



    # https://matplotlib.org/stable/gallery/pyplots/axline.html#sphx-glr-gallery-pyplots-axline-py