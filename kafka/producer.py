import random
import traceback
import json
from kafka import KafkaProducer


producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    client_id='5amsung',
    key_serializer=None,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'))


record = []
for i in range(10):
    record.append({
        'number': random.randint(0, 1000)
    })
try:
    response = producer.send(topic='5amsung', value=record).get()
except:
    traceback.print_exc()

print(response)