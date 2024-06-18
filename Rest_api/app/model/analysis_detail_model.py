from app.api import detail_api
from flask import current_app
from flask_restx import Namespace


def getNs() -> Namespace:
    return detail_api.ns


def select_community(es, id):
    res = es.search(index=current_app.config['CUSTOM_INDEX'],
                    body={
                        "_source": ["communities", "job_id"],
                        "size": 1,
                        "query": {
                          "bool": {
                              "must": [
                                  {
                                      "match": {
                                          "job_id": id
                                      }
                                  }
                              ]
                          }
                        },
                        "sort": [
                            {
                                "job_start_dt": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })

    if res['hits']['total']['value'] == 0:
        return None
    
    return res['hits']['hits'][0]


def select_media_count(es, id):
    res = es.search(index=current_app.config['CUSTOM_INDEX'],
                    body={
                        "_source": [
                          "media_count"
                        ],
                        "size": 1,
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "job_id": id
                                        }
                                    }
                                ]
                            }
                        },
                        "sort": [
                            {
                                "job_start_dt": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })

    if res['hits']['total']['value'] == 0:
        return None

    return res['hits']['hits'][0]


def select_issue_process(es, id):
    res = es.search(index=current_app.config['CUSTOM_INDEX'],
                    body={
                        "_source": [
                          "issue_process"],
                        "size": 1,
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "job_id": id
                                        }
                                    }
                                ]
                            }
                        },
                        "sort": [
                            {
                                "job_start_dt": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })

    if res['hits']['total']['value'] == 0:
        return None

    return res['hits']['hits'][0]


def select_wordcloud(es, id):
    res = es.search(index=current_app.config['CUSTOM_INDEX'],
                    body={
                        "_source": [
                          "wordcloud"],
                        "size": 1,
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "job_id": id
                                        }
                                    }
                                ]
                            }
                        },
                        "sort": [
                            {
                                "job_start_dt": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })
    
    if res['hits']['total']['value'] == 0:
        return None

    return res['hits']['hits'][0]


def select_senti_graph(es, id):
    res = es.search(index=current_app.config['CUSTOM_INDEX'],
                    body={
                        "_source": [
                          "senti_graph"],
                        "size": 1,
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "job_id": id
                                        }
                                    }
                                ]
                            }
                        },
                        "sort": [
                            {
                                "job_start_dt": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })
    

    if res['hits']['total']['value'] == 0:
        return None

    return res['hits']['hits'][0]

def select_media_count(es, id):
    res = es.search(index=current_app.config['CUSTOM_INDEX'],
                    body={
                        "_source": [
                          "media_count"
                        ],
                        "size": 1,
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "job_id": id
                                        }
                                    }
                                ]
                            }
                        },
                        "sort": [
                            {
                                "job_start_dt": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })

    if res['hits']['total']['value'] == 0:
        return None

    return res['hits']['hits'][0]
