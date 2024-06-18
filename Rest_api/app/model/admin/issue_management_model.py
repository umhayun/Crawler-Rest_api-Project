from flask import current_app

def issue_dates(es):
    res = es.search(index='auto-ranking',
                            body={
                                "track_total_hits": True,
                                "size": 0,
                                "aggs": {
                                    "dates": {
                                        "terms": {
                                            "field": "job_start_dt",
                                            "order": {
                                                "_key": "desc"
                                            },
                                            "size" : 60
                                        }
                                    }
                                }
                            })
    dates = res["aggregations"]["dates"]["buckets"]
    result = []
    for date in dates:
        result.append(date["key_as_string"])
    return result

def issue_data_by_date(es, date):
    res = es.search(index='auto-ranking',
                            body={
                                "track_total_hits": True,
                                "query": {
                                    "match": {
                                        "job_start_dt": date
                                    }
                                }
                            })
    return res['hits']['hits'][0]

def issue_update_by_num(es, _id, summary):
    res = es.update(index='auto-ranking',
                            id=_id,
                            body={
                                "doc": {
                                    "summary": summary
                                }
                            })
    return res