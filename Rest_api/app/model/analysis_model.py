from app.api import main_api
from flask import current_app
from flask_restx import Namespace


def getNs() -> Namespace:
    return main_api.ns


def select_analysis_count(es, query, media, start, end):

    media_list = media.split(",")
    res = es.search(index=current_app.config['EMBEDDING_INDEX']+'-*',
                    body={
                        "size": 0,
                        "track_total_hits": True,
                        "query": {
                          "bool": {
                              "must": [
                                  {
                                      "range": {
                                          "date": {
                                              "gte": start,
                                              "lte": end
                                          }
                                      }
                                  },
                                  {
                                      "match": {
                                          "embedding": "Yes"
                                      }
                                  },
                                  {
                                      "query_string": {
                                          "default_field": "text",
                                          "query": query
                                      }
                                  },
                                  {
                                      "terms": {
                                          "media": media_list
                                      }
                                  }

                              ]
                          }
                        }
                    })
    return res['hits']['total']
