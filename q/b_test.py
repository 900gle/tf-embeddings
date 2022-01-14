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
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['paragraph_vector']) + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }

    search_start = time.time()
    response = client.search(
        index=INDEX_NAME,
        body={
            "size": SEARCH_SIZE,
            "query": script_query,
            "_source": {"includes": ["title", "paragraph"]}
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
    INDEX_NAME = "products_multi"
    INDEX_FILE = "../data/posts/index.json"

    SEARCH_SIZE = 3

    print("Downloading pre-trained embeddings from tensorflow hub...")
    module_url = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
    print("module %s loaded" % module_url)
    model = hub.load(module_url)

    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    run_query_loop()

    print("Done.")