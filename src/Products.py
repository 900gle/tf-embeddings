import json
import time

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# Use tensorflow 1 behavior to match the Universal Sentence Encoder
# examples (https://tfhub.dev/google/universal-sentence-encoder/2).
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
##### INDEXING #####

def index_data():
    print("Creating the 'products' index.")
    client.indices.delete(index=INDEX_NAME, ignore=[404])

    with open(INDEX_FILE) as index_file:
        source = index_file.read().strip()
        client.indices.create(index=INDEX_NAME, body=source)

    docs = []
    count = 0

    with open(DATA_FILE) as data_file:
        for line in data_file:
            line = line.strip()

            doc = json.loads(line)
            # if doc["type"] != "question":
            #     continue

            docs.append(doc)
            count += 1

            if count % BATCH_SIZE == 0:
                index_batch(docs)
                docs = []
                print("Indexed {} documents.".format(count))

        if docs:
            index_batch(docs)
            print("Indexed {} documents.".format(count))

    client.indices.refresh(index=INDEX_NAME)
    print("Done indexing.")

def index_batch(docs):
    names = [doc["name"] for doc in docs]
    name_vectors = embed_text(names)

    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME
        request["name_vector"] = name_vectors[i]
        requests.append(request)
    bulk(client, requests)

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
                "source": "cosineSimilarity(params.query_vector, doc['name_vector']) + 1.0",
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
            "_source": {"includes": ["name", "price"]}
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

def embed_text(text):
    vectors = session.run(embeddings, feed_dict={text_ph: text})
    return [vector.tolist() for vector in vectors]

##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME = "products"
    INDEX_FILE = "data/products/index.json"

    DATA_FILE = "data/products/products.json"
    BATCH_SIZE = 1000

    SEARCH_SIZE = 5

    GPU_LIMIT = 0.5

    print("Downloading pre-trained embeddings from tensorflow hub...")
    embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
    text_ph = tf.placeholder(tf.string)

    embeddings = embed(text_ph)
    print("Done.")

    print("Creating tensorflow session...")
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = GPU_LIMIT
    session = tf.Session(config=config)
    session.run(tf.global_variables_initializer())
    session.run(tf.tables_initializer())
    print("Done.")

    client = Elasticsearch(http_auth=('elastic', 'dlengus'))

    index_data()
    run_query_loop()

    print("Closing tensorflow session...")
    session.close()
    print("Done.")
