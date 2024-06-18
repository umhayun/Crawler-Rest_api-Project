from flask_restx import Namespace
from app.api import main_api


def getNs() -> Namespace:
    return main_api.ns


def select_weekly_rank(es):
    res = es.search(index='auto-ranking',
                    body={
                        "size": 1,
                        "sort": [
                            {
                                "job_start_dt": {
                                    "order": "desc"
                                }
                            }
                        ]
                    })
    result = res['hits']['hits'][0]
    return result


def select_daily_rank(es, search_date):

    res = es.search(index='auto-ranking',
                    body={
                        "size": 5,
                        "query": {
                            "terms": {
                                "job_start_dt": search_date
                            }

                        }, "sort": [
                            {
                                "job_start_dt": {
                                    "order": "desc"
                                }
                            }
                        ]
                    }
                    )

    return res


def select_detail(es, num):
    res = es.search(index='auto-detail',
                    body={
                        "_source": ["graph", "summary"],
                        "size": 1,
                        "query": {
                          "bool": {
                              "must": [
                                  {
                                      "match_all": {}
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
    result = res['hits']['hits'][0]
    return result
