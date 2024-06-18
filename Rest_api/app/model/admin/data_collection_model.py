from datetime import datetime
from flask import current_app


def comment_total_by_media(es):
    res = es.search(index='embedding-*',
                    body=
                    {
                    "track_total_hits": True,
                    "size":0,
                    "aggs": {
                        "comment_total": {
                        "terms": {
                            "field": "type.keyword",
                            "include": "comment",
                            "min_doc_count": 0,
                            "size": 2
                            },
                            "aggs": {
                                "media_total": {
                                "terms": {
                                "field": "media.keyword",
                                "size": 10,
                                "min_doc_count" : 0,
                                "order": {
                                    "_key": "asc"
                                    }
                                }
                                }
                            }
                        }
                        }
                    }
                    )
    data = res['aggregations']['comment_total']['buckets'][0]
    #data = res['aggregations']
    lists = data['media_total']['buckets']
    total = data['doc_count']
    res_dic = {}
    res_list = []
    naver_cnt = 0
    for list in lists:
        media_dict = {}
        if '네이버' in list['key']:
            naver_cnt += list['doc_count']
            continue
        if '디시인싸이드' == list['key']:
            continue
        media_dict['name'] = list['key']
        media_dict['value'] = list['doc_count']
        res_list.append(media_dict)
    res_list.insert(0, {'name': '네이버', 'value': naver_cnt})
    res_dic['total'] = total
    res_dic['data'] = res_list
    return res_dic


def comment_total_by_date(es, start, end):
    res = es.search(index='embedding-*',
                    body={
                        "track_total_hits": True,
                        "size": 0,
                        "query": {
                            "range": {
                                "date": {
                                    "gte": start,
                                    "lte": end,
                                    "relation": "within",
                                    "time_zone": "+09:00"
                                }
                            }
                        },
                        "aggs": {
                        "comment_total": {
                        "terms": {
                            "field": "type.keyword",
                            "include": "comment",
                            "min_doc_count": 0,
                            "size": 2
                            },
                        "aggs": {
                            "media_total": {
                                "terms": {
                                    "field": "media.keyword",
                                    "min_doc_count": 0,
                                    "order": {
                                        "_key": "asc"
                                    }
                                },
                                "aggs": {
                                    "date_total": {
                                        "date_histogram": {
                                            "field": "date",
                                            "calendar_interval": "day",
                                            "time_zone": "+09:00",
                                            "order": {
                                                "_key": "asc"
                                            },
                                            "extended_bounds": {
                                                "min": start,
                                                "max": end
                                            },
                                        }
                                    }
                                }
                            }
                            }
                        }
                    }
                }
                    )

    data = res['aggregations']['comment_total']
    comment_total = data['buckets'][0]['doc_count']
    lists = data['buckets'][0]['media_total']['buckets']
    # data = res['aggregations']['media_total']
    # lists = data['buckets']
    res_list = []
    date_list = ['product']
    naver_list = []
    res_dic = {}
    for list in lists:
        media_list = []
        key = list['key']
        if '네이버' in key:
            for idx, val in enumerate(list['date_total']['buckets']):
                l = len(naver_list)

                if l == idx:
                    naver_list.append(val['doc_count'])
                else:
                    naver_list[idx] += val['doc_count']
        elif '디시인싸이드' == key:
            continue
        else:
            for ml in list['date_total']['buckets']:
                count = ml['doc_count']
                media_list.append(count)
                if len(res_list) == 0:
                    date = datetime.strptime(ml['key_as_string'], '%Y-%m-%dT00:00:00.000+09:00').strftime('%m-%d')
                    date_list.append(date)
            media_list.insert(0, key)
            res_list.append(media_list)

    res_list.append(date_list)
    naver_list.insert(0, '네이버')
    res_list.append(naver_list)
    res_list.sort()
    res_dic['total'] = comment_total
    # res_dic['total'] = res['hits']['total']['value']
    res_dic['data'] = res_list

    return res_dic


def post_total_by_media(es):
    res = es.search(index='crawling-*',
                    body={
                        "track_total_hits": True,
                        "size": 0,
                        "aggs": {
                            "post_total": {
                                "terms": {
                                    "field": "media.keyword",
                                    "size": 10,
                                    "min_doc_count": 0,
                                    "order": {
                                        "_key": "asc"
                                    }
                                }
                            }
                        }
                    })

    datas = res['aggregations']['post_total']['buckets']
    total = res['hits']['total']['value']
    res_dic = {}
    res_list = []
    naver_cnt = 0
    for data in datas:
        media_dict = {}
        if '네이버' in data['key']:
            naver_cnt += data['doc_count']
            continue
        if '디시인싸이드' == data['key']:
            continue
        media_dict['name'] = data['key']
        media_dict['value'] = data['doc_count']
        res_list.append(media_dict)
    res_list.insert(0, {'name': '네이버', 'value': naver_cnt})
    res_dic['total'] = total
    res_dic['data'] = res_list

    return res_dic


def post_total_by_date(es, start, end):
    res = es.search(index='crawling-*',
                    body={
                        "track_total_hits": True,
                        "size": 0,
                        "query": {
                            "range": {
                                "date": {
                                    "gte": start,
                                    "lte": end,
                                    "relation": "within",
                                    "time_zone": "+09:00"
                                }
                            }
                        },
                        "aggs": {
                            "post_total": {
                                "terms": {
                                    "field": "media.keyword",
                                    "size": 10,
                                    "min_doc_count": 0,
                                    "order": {
                                        "_key": "asc"
                                    }
                                },
                                "aggs": {
                                    "date_total": {
                                        "date_histogram": {
                                            "field": "date",
                                            "time_zone": "+09:00",
                                            "calendar_interval": "day",
                                            "order": {
                                                "_key": "asc"
                                            },
                                            "extended_bounds": {
                                                "min": start,
                                                "max": end
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    })

    lists = res['aggregations']['post_total']['buckets']
    post_total = res['hits']['total']['value']

    res_list = []
    res_dic = {}
    date_list = ['product']
    naver_list = []
    for list in lists:
        media_list = []
        key = list['key']
        if '네이버' in key:
            for idx, val in enumerate(list['date_total']['buckets']):
                l = len(naver_list)
                if l == idx:
                    naver_list.append(val['doc_count'])
                else:
                    naver_list[idx] += val['doc_count']
        elif '디시인싸이드' in key:
            continue
        else:
            for ml in list['date_total']['buckets']:
                count = ml['doc_count']
                media_list.append(count)
                if len(res_list) == 0:
                    date = datetime.strptime(ml['key_as_string'], '%Y-%m-%dT00:00:00.000+09:00').strftime('%m-%d')
                    date_list.append(date)
            media_list.insert(0, key)
            res_list.append(media_list)
    naver_list.insert(0, '네이버')
    res_list.append(naver_list)
    res_list.insert(0, date_list)
    res_list.sort()
    res_dic['total'] = post_total
    res_dic['data'] = res_list

    return res_dic
