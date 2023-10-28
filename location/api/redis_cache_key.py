# -*- coding: utf-8 -*-
import time

import requests
import ssl
import urllib3
import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
import numpy as np

print(ssl.OPENSSL_VERSION)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##### SEARCHING #####

def run_query_loop():

    for i in range(1, 10000):
        query_a(i)
        print(i)


def query_a(index):
    url_api = "http://localhost:8080/api/search/distance?distance="+ str(index) +"&countryCode=KR&from=0&size=10"
    response = requests.get(url_api, verify=False)
    print(response)

##### MAIN SCRIPT #####

if __name__ == '__main__':
    run_query_loop()
    print("Done.")
