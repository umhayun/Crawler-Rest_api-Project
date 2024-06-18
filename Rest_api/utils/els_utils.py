from elasticsearch import Elasticsearch
from flask import current_app


class ELSUtils:
    def __init__(self):
        hosts = current_app.config['ELASTICSEARCH_URL'].split(', ')
        port = ":" + str(current_app.config['ELASTICSEARCH_PORT'])
        hosts = [s + port for s in hosts]
        self.es = Elasticsearch(hosts)
    
    def getConn(self):
        return self.es

    def closeEs(self):
        self.es.close()