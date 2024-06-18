# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from elasticsearch import Elasticsearch
from elasticsearch.client import IngestClient
from scrapy.utils.project import get_project_settings

import pymysql
import logging
from datetime import datetime
from konlpy.tag import Okt
from kss import split_sentences
import traceback

from blogCrawler.log_util import LogUtil
from blogCrawler.preprocessor import preprocessor


class NaverPipeline:
    crawled_count = 0
    duplicate_count = 0
    new_comments = 0
    is_first = True

    def __init__(self):
        self.settings = get_project_settings()

        self.url = "%s:%d" % (self.settings['ELASTICSEARCH_SERVER'], self.settings['ELASTICSEARCH_PORT'])
        self.es=Elasticsearch(hosts=self.url)

        self.naver_mapping = {
                                "settings": {
                                    "number_of_shards": 1,
                                    "number_of_replicas": 1
                                },
                                "mappings": {
                                    "properties":{
                                        "url":{
                                            "type":"text",
                                            "fields" : {
                                                "keyword":{
                                                "type":"keyword",
                                                "ignore_above":10000
                                                }
                                            }
                                        }
                                    }
                                }
                            }
        self.embedding_mapping = {
                                "settings": {
                                    "number_of_shards": 1,
                                    "number_of_replicas": 1
                                },  "mappings": {
                                    "properties":{
                                        "url":{
                                            "type":"text",
                                            "fields" : {
                                                "keyword":{
                                                "type":"keyword",
                                                "ignore_above":10000
                                                }
                                            }
                                        }
                                    }
                                }
                            }

        self.okt = Okt()


    def process_item(self, item, spider): 
        
        if self.is_first: # argv를 받으려면 여기서 해야만 함 
            log_util = LogUtil('naverBlogCrawler' + '-' + str(spider.sub_id))
            self.log = log_util.get_logger()  # Scrapy에 logger가 정의되어 있어서 self.logger 사용 못함 

            self.preproc = preprocessor(self.log)
            self.preproc.load_stop_word()
            self.is_first = False

        doc = dict(item)     
        self.job_id = doc['job_id']
        index_date = datetime.strptime(doc['date'],'%Y-%m-%dT%H:%M:%S+09:00').strftime('%Y%m')
        self.naver_index = f"crawling-naver-blog-{index_date}"

        if self.es.indices.exists(index = self.naver_index):
            pass
        else:
            self.es.indices.create(index = self.naver_index,body=self.naver_mapping)

        client = IngestClient(self.es)
        settings = {
            "description": "Adds a field to a document with the time of ingestion",
            "processors": [
                {
                    "set": {
                        "field": "@timestamp",
                        "value": "{{_ingest.timestamp}}"
                    }
                }
            ]
        }
        client.put_pipeline(id='timestamp', body=settings)

        res = self.es.search(
            index = self.naver_index,
            body =
            {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "url.keyword": doc['url']                   
                                }

                            }
                        ]
                    }
                }
            }
        )

        self.crawled_count = self.crawled_count + 1

        # 데이터 확인 후 insert or update
        if res['hits']['total']['value'] == 0:             
            self.es.index(index=self.naver_index, body=doc, pipeline='timestamp')
        else:      
            self.es.update_by_query(pipeline='timestamp',index=self.naver_index,body={
                "script":{
                    "source": "ctx._source = params.data",
                    "params": {
                    "data":doc 
                    }
                    },
                    "query":{
                        "bool":{
                        "filter": [
                            {
                            "term":{
                                "url.keyword":doc['url']
                            }
                            }
                        ] 
                        }
                        
                    }                 
                })

            self.duplicate_count = self.duplicate_count + 1
        
        self.log.debug("crawled item: " + str(self.crawled_count))
        self.log.debug("duplicated item: " + str(self.duplicate_count))
        try: 
            self.process_embedding(doc)
        except Exception as e:
            self.log.error ('process_embedding exception: ' + str(e))
            self.log.error (traceback.print_exc())

        self.log.debug("new comments: " + str(self.new_comments))

        return item
    

    def process_embedding(self, doc): 

        #
        # title 처리
        #

        # 1. title이 stopword에 포함되면 더이상 처리안함 
        if self.preproc.check_stop_word(doc['title']):
            return
        
        # 2. title에서 특수문자를 지움 
        doc['title'] = self.preproc.delete_special_word(doc['title'])
        self.log.debug ('after delete special word: ' + doc['title'])

        # 3. title의 단어가 4글자 보다 작으면 title 처리 안함 
        if len(doc['title'].split()) >= 4:

            # 4. title 형태소 분석 
            words = list()
            nouns = self.okt.nouns(doc['title'])
            words.extend(nouns)
            for noun in nouns:
                if len(noun) == 1:
                    words.remove(noun)

            # 5. 저장할 포멧으로 변경 
            title_doc = dict()
            title_doc['id'] = 'nbt-'+ doc['url'].split('/')[-2] + doc['url'].split('/')[-1] # naver blog title 
            title_doc['url'] = doc['url']
            title_doc['date'] = doc['date']
            title_doc['keywords'] = doc['keywords']
            title_doc['text'] = doc['title']
            title_doc['media'] = doc['media']
            title_doc['writer'] = doc['writer']
            title_doc['type'] = 'title'
            title_doc['analyzed_words'] = words
            title_doc['num_like'] = doc['like']
            title_doc['num_dislike'] = 0
            title_doc['num_view'] = 0
            title_doc['num_reply'] = len(doc['comment'])
            title_doc['embedding'] = 'No'

            # 6. 기존 인덱스에 해당 블로그 id가 존재하는 확인 (인덱스가 없으면 생성)
            index_date=datetime.strptime(title_doc['date'],'%Y-%m-%dT%H:%M:%S+09:00').strftime('%Y%m%d')
            self.embedding_index=f"embedding-{index_date}"

            if self.es.indices.exists(index = self.embedding_index):
                pass
            else:
                self.es.indices.create(index = self.embedding_index,body=self.embedding_mapping)
                
            client = IngestClient(self.es)
            settings = {
                "description": "Adds a field to a document with the time of ingestion",
                "processors": [
                    {
                        "set": {
                            "field": "@timestamp",
                            "value": "{{_ingest.timestamp}}"
                        }
                    }
                ]
            }
            client.put_pipeline(id='timestamp', body=settings)

            res = self.es.search(
                index = 'embedding*',
                body =
                {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "id.keyword": title_doc['id']                   
                                    }
                                }
                            ]
                        }
                    }
                }
            )

            # 7. 신규 document를 저장 
            if res['hits']['total']['value'] == 0:             
                self.es.index(index=self.embedding_index, body=title_doc, pipeline='timestamp')

        else: 
            self.log.debug ('title: "' + doc['title'] + '" length is less than 4')
             

        #
        # comment 처리
        #

        for comment in doc['comment']: 

            # 1. comment가 빈문자열이면 처리 안함 
            if len(comment) < 1: 
                continue

            # 2. comment의 text를 각 줄별로 분리해서 comment_texts 생성
            comment_texts = split_sentences(comment['text'])

            for comment_text in comment_texts: 

                # 3. comment_text에서 특수 문자를 지움 (주: comment_text에 대해서는 stopword 처리는 안함) 
                comment_text = self.preproc.delete_special_word(comment_text)
                self.log.debug ('after delete special word: ' + str(comment_text))
                if comment_text == None: 
                    continue

                # 4. comment_text에서 not_comment 문자열이 있으면 처리 안함 
                if self.preproc.check_not_comment_word(comment_text):
                    continue

                #comment_text = self.spacing(comment_text) 띄어쓰기 라이브러리 검토 필요 
                #print ('after spacing: ' + comment_text) 

                # 5. comment_text의 단어가 4글자 보다 작으면 처리 안함 
                if len(comment_text.split()) >= 4:

                    # 6. sub_comment 형태소 분석 
                    words = list()
                    try:
                        nouns = self.okt.nouns(comment_text)
                        words.extend(nouns)
                        for noun in nouns:
                            if len(noun) == 1:
                                words.remove(noun)
                    except Exception as e:
                        self.log.error('error: ' + str(e))
                        self.log.error (traceback.print_exc())
                        continue

                    # 7. 저장할 포멧으로 변경 
                    comment_doc = dict()
                    comment_doc['id'] = 'nbc-'+ doc['url'].split('/')[-2] + comment['id'] # naver blog comment
                    comment_doc['url'] = doc['url']
                    comment_doc['date'] = comment['date']
                    comment_doc['keywords'] = doc['keywords']
                    comment_doc['text'] = comment_text
                    comment_doc['media'] = doc['media']
                    comment_doc['writer'] = comment['nickname']
                    comment_doc['type'] = 'comment'
                    comment_doc['analyzed_words'] = words
                    comment_doc['num_like'] = doc['like']
                    comment_doc['num_dislike'] = 0
                    comment_doc['num_view'] = 0
                    comment_doc['num_reply'] = len(doc['comment'])
                    comment_doc['embedding'] = 'No'

                    # 8. 기존 인덱스에 해당 블로그 id가 존재하는 확인 (인덱스가 없으면 생성)
                    index_date = datetime.strptime(comment_doc['date'],'%Y-%m-%dT%H:%M:00+09:00').strftime('%Y%m%d')
                    self.embedding_index = f"embedding-{index_date}"

                    if self.es.indices.exists(index = self.embedding_index):
                        pass
                    else:
                        self.es.indices.create(index = self.embedding_index,body=self.embedding_mapping)
                        
                    client = IngestClient(self.es)
                    settings = {
                        "description": "Adds a field to a document with the time of ingestion",
                        "processors": [
                            {
                                "set": {
                                    "field": "@timestamp",
                                    "value": "{{_ingest.timestamp}}"
                                }
                            }
                        ]
                    }
                    client.put_pipeline(id='timestamp', body=settings)

                    res = self.es.search(
                        index = self.embedding_index,
                        body =
                        {
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                            "match": {
                                                "id.keyword": comment_doc['id']                   
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    )

                    # 9. 신규 document를 저장 
                    if res['hits']['total']['value'] == 0:             
                        self.es.index(index=self.embedding_index, body=comment_doc, pipeline='timestamp')
                        self.new_comments += 1

                else: 
                    self.log.debug ('comment: "' + comment_text + '" length is less than 4')

    def close_spider(self,spider):
        if self.crawled_count != 0: 
            self.conn = pymysql.connect(
            host = self.settings['MARIADB_HOST'],
            port = self.settings['MARIADB_PORT'],
            user = self.settings['MARIADB_USERNM'],
            password = self.settings['MARIADB_PASSWD'],
            db = self.settings['MARIADB_DBNM'], 
            charset = 'utf8')
            self.cur = self.conn.cursor()
            query_str = f"UPDATE CRAWLER_STATUS SET data_count = {self.crawled_count} where job_id = '{self.job_id}'" 
            self.log.debug ('query_string: ' + str(query_str))
            self.cur.execute(query_str)
            self.log.debug ('total : '+str(self.crawled_count))
            self.conn.commit()

