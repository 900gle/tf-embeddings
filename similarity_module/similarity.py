from elasticsearch import Elasticsearch
import pprint as ppr
import json
import math

import matplotlib.pyplot as plt
import numpy as np

index_name1 = "script-similarity-index1"
index_name2 = "script-similarity-index2"
index_name3 = "script-similarity-index3"

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
        with open("/data/products/similarity_data.json", "r", encoding="utf-8") as fjson:
            data = json.loads(fjson.read())

            for n, i in enumerate(data):
                doc = {
                    "name": i['name']
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
        SEARCH_SIZE=100
        MAX_SCORE = 5

        query1 = {
            "size" : SEARCH_SIZE,
            "query": {
                "match": {
                    "name" : keyword
                }
            }
        }
        query2 = {
            "size" : SEARCH_SIZE,
            "query": {
                "match": {
                    "name" : keyword
                }
            }
        }
        query3 = {
            "size" : SEARCH_SIZE,
            "query": {
                "match": {
                    "name" : keyword
                }
            }
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
        script1 = "double tf = Math.sqrt(doc.freq); double idf = Math.log((field.docCount+1.0)/(term.docFreq+1.0)) + 1.0; double norm = 1/Math.sqrt(doc.length); return query.boost * tf * idf * norm;"
        EsAPI.createIndex(script1, index_name1)
        script2 = "double tf = Math.sqrt(doc.freq); double idf = Math.log(((field.docCount * 2)+1.0)/(term.docFreq+1.0)) + 1.0; double norm = 1/Math.sqrt(doc.length); return query.boost * tf * idf * norm;"
        EsAPI.createIndex(script2, index_name2)
        script3 = "double tf = Math.sqrt(doc.freq); double idf = Math.log((field.docCount+1.0)/(term.docFreq+1.0)) + 1.0; double norm = 1/Math.sqrt(doc.length * 2); return query.boost * tf * idf * norm;"
        EsAPI.createIndex(script3, index_name3)
    @classmethod
    def createIndex(cls, script, index_name):
        cls.es.indices.create(
            index=index_name,
            body={
                "settings": {
                    "number_of_replicas": 0,
                    "number_of_shards": 1,
                    "similarity": {
                        "scripted_tfidf": {
                            "type": "scripted",
                            "script": {
                                "source": script
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "name": {
                            "type": "text",
                            "similarity": "scripted_tfidf"
                        }
                    }
                }

            }
        )



# EsAPI.createIndexSet()
# EsAPI.dataInsert()
EsAPI.searchResult()

