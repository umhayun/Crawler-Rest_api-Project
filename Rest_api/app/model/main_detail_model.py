from flask_restx import Namespace
from app.api import main_api


def getNs() -> Namespace:
    return main_api.ns


def select_summary(es, match):

    res = es.search(index='auto-ranking',
                    body={
                        "_source": ["summary"],
                        "size": 1,
                        "query": {
                          "bool": {
                              "must": [
                                  match
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


def select_community(es, match):
    res = es.search(index='auto-detail',
                    body={
                        "_source": ["communities", "summary"],
                        "size": 1,
                        "query": {
                          "bool": {
                              "must": [
                                  match
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


def select_media_count(es, match):

    res = es.search(index='auto-detail',
                    body={
                        "_source": [
                          "media_count"
                        ],
                        "size": 1,
                        "query": {
                            "bool": {
                                "must": [
                                    match
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


def select_issue_process(es, match):
    res = es.search(index='auto-detail',
                    body={
                        "_source": [
                            "issue_process"],
                        "size": 1,
                        "query": {
                            "bool": {
                                "must": [
                                    match
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


def select_wordcloud(es, match):
    res = es.search(index='auto-detail',
                    body={
                        "_source": [
                            "wordcloud"],
                        "size": 1,
                        "query": {
                            "bool": {
                                "must": [
                                    match
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


def select_senti_graph(es, match):

    res = es.search(index='auto-detail',
                    body={
                        "_source": [
                            "senti_graph"],
                        "size": 1,
                        "query": {
                            "bool": {
                                "must": [
                                    match
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
