from elasticsearch import Elasticsearch
import pprint as ppr
import json
import math

import matplotlib.pyplot as plt
import numpy as np

index_name1 = "payload-sort-index1_t"
index_name2 = "payload-sort-index2_t"
index_name3 = "payload-sort-index3_t"


class EsAPI:
    es = Elasticsearch(hosts="localhost", port=9200, http_auth=('elastic', 'dlengus'))  # 객체 생성

    @classmethod
    def srvHealthCheck(cls):
        health = cls.es.cluster.health()
        print(health)

    @classmethod
    def allIndex(cls):  # Elasticsearch에 있는 모든 Index 조회
        print(cls.es.cat.indices())

    @classmethod
    def dataInsert(cls):
        # ===============
        # 데이터 삽입
        # ===============
        with open("/Users/doo/project/tf-embeddings/data/similarity_data.json", "r", encoding="utf-8") as fjson:
            data = json.loads(fjson.read())

            for n, i in enumerate(data):
                doc = {
                    "name": i['name'],
                    "keyword": i['keyword'],
                    # "rank": i['keyword'] + "|" + str(i['rank'])
                    "rank": "123_1" + "|" + str(i['rank'])

                }
                cls.es.index(index=index_name1, doc_type="_doc", id=n + 1, body=doc)
                cls.es.index(index=index_name2, doc_type="_doc", id=n + 1, body=doc)
                cls.es.index(index=index_name3, doc_type="_doc", id=n + 1, body=doc)

                print(i['name'])

        cls.es.indices.refresh(index=index_name1)
        cls.es.indices.refresh(index=index_name2)
        cls.es.indices.refresh(index=index_name3)
        print("done.")

    @classmethod
    def searchResult(cls):
        keyword = input("query : ")
        SEARCH_SIZE = 100
        MAX_SCORE = 5

        query1 = {
            "size": SEARCH_SIZE,
            "query": {
                "term": {
                    "keyword": {
                        "value": "고야드"
                    }
                }
            },
            "sort": [
                {
                    "_script": {
                        "script": {
                            "source": "payload_sort",
                            "lang": "sort_script",
                            "params": {
                                "field": "rank",
                                "value": "고야드"
                            }
                        },
                        "type": "number",
                        "order": "asc"
                    }
                }
            ]
        }

        query2 = {
            "size": SEARCH_SIZE,
            "query": {

                "term": {
                    "keyword": {
                        "value": "고야드"
                    }
                }

            },
            "sort": [
                {
                    "_script": {
                        "script": {
                            "source": "payload_score",
                            "lang": "sort_script",
                            "params": {
                                "field": "rank",
                                "value": "고야드"
                            }
                        },
                        "type": "number",
                        "order": "asc"
                    }
                }
            ]
        }
        query3 = {
            "size": SEARCH_SIZE,
            "query": {

                "term": {
                    "keyword": {
                        "value": "고야드"
                    }
                }

            },
            "sort": [
                {
                    "_script": {
                        "script": {
                            "source": "payload_score",
                            "lang": "sort_script",
                            "params": {
                                "field": "rank",
                                "value": "고야드"
                            }
                        },
                        "type": "number",
                        "order": "asc"
                    }
                }
            ]
        }

        x = np.arange(0, SEARCH_SIZE, 1)

        print(x)
        y1 = EsAPI.searchScore(query1, index_name1)
        print(y1)
        y2 = EsAPI.searchScore(query2, index_name2)
        print(y2)
        y3 = EsAPI.searchScore(query3, index_name3)
        print(y3)

        plt.xlim([1, len(y1)])  # X축의 범위: [xmin, xmax]
        plt.ylim([0, MAX_SCORE])  # Y축의 범위: [ymin, ymax]
        plt.xlabel('top 5', labelpad=2)
        plt.ylabel('score', labelpad=2)
        plt.plot(x, y1, label='match tf', color='#e35f62', marker='*', linewidth=1)
        plt.plot(x, y2, label='match idf', color='#333300', marker='*', linewidth=1)
        plt.plot(x, y3, label='match norm', color='#000000', marker='*', linewidth=1)

        plt.legend()
        plt.title('Query score')
        plt.xticks(x)
        plt.yticks(np.arange(1, MAX_SCORE))
        plt.grid(True)
        plt.show()

    @classmethod
    def searchScore(cls, query, index_name):
        response = cls.es.search(
            index=index_name,
            body=query
        )

        return [hit["_score"] for hit in response["hits"]["hits"]]

    @classmethod
    def createIndexSet(cls):
        EsAPI.createIndex(index_name1)
        EsAPI.createIndex(index_name2)
        EsAPI.createIndex(index_name3)

    @classmethod
    def createIndex(cls, index_name):
        cls.es.indices.create(
            index=index_name,
            body={
                "settings": {
                    "number_of_replicas": 0,
                    "number_of_shards": 1,
                    "analysis": {
                        "analyzer": {
                            "payload_delimiter": {
                                "filter": [
                                    "delimited_payload"
                                ],
                                "encoding": "identity",
                                "delimiter": "|",
                                "tokenizer": "whitespace"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "rank": {
                            "type": "text",
                            "term_vector": "with_positions_payloads",
                            "analyzer": "payload_delimiter"
                        }
                    }
                }

            }
        )


# EsAPI.createIndexSet()
EsAPI.dataInsert()
# EsAPI.searchResult()
