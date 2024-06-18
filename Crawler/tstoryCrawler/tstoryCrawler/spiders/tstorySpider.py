import sys
import scrapy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from scrapy.utils.project import get_project_settings
import secrets
import time
import pymysql
import math
import json 
import traceback
import re
from fake_useragent import UserAgent

from tstoryCrawler.items import TstorycrawlerItem
from dateutil.relativedelta import relativedelta
from tstoryCrawler.log_util import LogUtil

import requests


class TstorySpider(scrapy.Spider):
    name = 'tstorySpider'
    
    url = 'https://tistory.com/m/api/search/posts?keyword={}&sort=RECENCY&page=1'
    

    def __init__(self, job_id='', sub_id='', *args, **kwargs):
        super(TstorySpider, self).__init__(*args, **kwargs)

        self.settings = get_project_settings()
         
        # 실행 정보 확인 
        # job_id는 한번에 실행되는 job의 단위, sub_id는 실행되는 crawler별로 생성
        self.job_id = job_id
        self.sub_id = sub_id 
       
        log_util = LogUtil('tstoryCrawler' + '-' + str(sub_id))
        self.log = log_util.get_logger()  # Scrapy에 logger가 정의되어 있어서 self.logger 사용 못함 
        
        self.init_mysql()

        # 검색 키워드
        self.filtering_keywords = self.get_keyword()
        #검색 상세조건
        query_str = "SELECT * FROM CRAWLER_STATUS where job_id = '{}' and sub_id = '{}'".format(job_id, sub_id)
        self.log.debug ('query_string: ' + query_str)
        self.cur.execute(query_str)
        res = self.cur.fetchall()

        if len(res) != 1: 
            self.log.error('len(res) is ' + str(len(res)))
            self.quit_self('len(res) is ' + str(len(res)))

        try: 
            for cursor in res:
                self.log.debug(res)
                self.job_type = cursor[2]
                self.status = cursor[5]
                self.keywords = cursor[6].split(',') # 검색어 리스트 
                self.period = int(cursor[7])
                self.start_date = cursor[8]
                self.end_date = cursor[9]
                self.start_index = int(cursor[10])
                self.end_index = int(cursor[11])
                break
        except Exception as e:
            self.log.error('error: ' + str(e))
            self.log.error (traceback.print_exc())
            self.quit_self('db error')
        
        # auto 일때는 I 또는 C에서 period를 보고 실행한다. 
        if self.job_type == 'A': 
            
            # 이미 돌고 있으면 종료 한다. 
            if self.status == 'S': 
                self.quit_self('previous job is running ')
                
            elif self.status == 'I' or self.status == 'C': 
                cur_date = datetime.today()
                start_date_str = (cur_date - relativedelta(days=self.period)).strftime('%Y-%m-%d 00:00:00')
                end_date_str = cur_date.strftime('%Y-%m-%d 23:59:59')
                self.start_date = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
                self.end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
                query_str = "UPDATE CRAWLER_STATUS SET status = 'S', search_start_date = '" + self.start_date.strftime('%Y-%m-%d %H:%M:%S') + \
                        "', search_end_date = '" + self.end_date.strftime('%Y-%m-%d %H:%M:%S') + "', crawler_start_date = '" + cur_date.strftime('%Y-%m-%d %H:%M:%S') + \
                        "', crawler_end_date = null, update_date = '" + cur_date.strftime('%Y-%m-%d %H:%M:%S') + "' where job_id = '{}' and sub_id = '{}'".format(job_id, sub_id)

                self.log.debug (query_str)
                self.cur.execute (query_str)
                self.conn.commit ()
                
            else:
                self.quit_self('unknown status')

        else: 
            cur_date = datetime.today()
            query_str = "UPDATE CRAWLER_STATUS SET status = 'S', crawler_start_date = '" + cur_date.strftime('%Y-%m-%d %H:%M:%S') + \
                    "', update_date = '" + cur_date.strftime('%Y-%m-%d %H:%M:%S') + \
                    "' where job_id = '{}' and sub_id = '{}'".format(job_id, sub_id)
            self.log.debug (query_str)
            self.cur.execute (query_str)
            self.conn.commit ()
        
        self.secretsGenerator = secrets.SystemRandom()
       
        
    def start_requests(self):   
        tstory_id_dic = self.get_url_list()
        
        self.log.debug ('tstory_id_dic: ' + str(len(tstory_id_dic)))

        for url, content_dic in tstory_id_dic.items():
            yield scrapy.Request(url=url, callback=self.parse_tstory, meta=content_dic)

            
    def get_url_list(self):
        self.start_page = math.ceil(self.start_index / 30) # 페이지당 30개
        self.end_page = math.ceil(self.end_index / 30) 
        self.log.debug ('start_date: ' + str(self.start_date))
        self.log.debug ('end_date: ' + str(self.end_date))
        self.log.debug ('start_page: ' + str(self.start_page))
        self.log.debug ('end_page: ' + str(self.end_page))
        manual_num = 0
        tstory_id_dic = dict()
        previous_dic_count = 0
        for filtering_keyword in self.filtering_keywords:
            if self.job_type == "M":
                manual_num += 1
                if manual_num > 1:
                    break     
                filtering_keyword['search_keyword'] = self.keywords
                self.log.debug ('topic: ' + str(filtering_keyword['search_keyword']))
            else:
                self.log.debug ('topic: ' + filtering_keyword['topic'])
            for keyword in filtering_keyword['search_keyword']:
                url = self.url.format(keyword)
                page = 1  
                is_finished = False 
                    
                while True:
                    self.log.debug (url)

                    res = requests.get(url)
                    res_dic = json.loads(res.text)
                
                    contents = res_dic['data']['searchedEntries']
                    for content in contents:
                        try: 
                            '''
                            {"blogId":6609893,"blogTitle":"Counselor B","blogUrl":"https://counselorb.tistory.com/m",
                            "entrySummary":"몇 년 전 운석이 떨어져 집이 붕괴되었지만 해당 운석은 수 지구에 떨어질 때 과정...",
                            "entryUrl":"https://counselorb.tistory.com/m/7","entryThumbnail":"https://blog.kakaocdn.net/dn/WGruB/btssVHGA4Q6/ONqnTJ1j1VuxrJbiJCRqV0/img.jpg",
                            "entryPublished":"2023-09-10T02:00:11+09:00","likeCount":0,"commentCount":0,"agoPublished":"12시간 전"}
                            '''
                            content_date = datetime.strptime(content['entryPublished'], '%Y-%m-%dT%H:%M:%S+09:00')
                            if content_date < self.start_date: # 검색 기간보다 전의 데이터 나오면 종료 
                                is_finished = True
                                self.log.debug ('content_date "' + str(content_date) + '" < start_date "' + str(self.start_date) + '"')
                                break
                            elif content_date > self.end_date: # 검색 기간보다 최근의 데이터 나오면 계속 확인  
                                self.log.debug ('content_date "' + str(content_date) + '" > start_date "' + str(self.end_date) + '"')
                                continue 
                                                
                            content_title = content['entryTitle']
                            if self.job_type == "M":
                                if keyword in content_title:
                                    content_url = content['entryUrl']                        
                                    content_dic = tstory_id_dic.get(content_url)
                                    if content_dic == None:
                                        content_dic = {}
                                        content_dic['url'] = content['entryUrl']
                                        content_dic['blog_id'] = content['blogId']
                                        content_dic['keywords'] = keyword
                                        #content_dic['media'] = '티스토리'
                                        content_dic['title'] = content['entryTitle']
                                        #content_dic['writer'] = '' # 이거때문에 화면 로딩해야 함 
                                        content_dic['date'] = content['entryPublished']
                                        #content_dic['content'] = ''
                                        content_dic['like'] = content['likeCount']
                                        content_dic['comment_count'] = content['commentCount']

                                        tstory_id_dic[content_url] = content_dic
                                    else:
                                        self.log.debug ('tstory_id_dic[url] exist: ' + content_url)
                            else :
                                for must_in_kr in filtering_keyword['must_in_kr']:
                                    # 필수키워드
                                    if must_in_kr not in content_title:
                                        continue
                                    # 제외키워드                      
                                    match_out_kr = re.match(filtering_keyword['must_out_kr'], content_title)
                                    if match_out_kr is not None:
                                        continue
                                    # 포함키워드
                                    if filtering_keyword['must_co_kr'] is not None:
                                        match_co_kr = re.match(filtering_keyword['must_co_kr'], content_title)
                                        if match_co_kr is None:
                                            continue
                                    content_url = content['entryUrl']                        
                                    content_dic = tstory_id_dic.get(content_url)
                                    if content_dic == None:
                                        content_dic = {}
                                        content_dic['url'] = content['entryUrl']
                                        content_dic['blog_id'] = content['blogId']
                                        content_dic['keywords'] = keyword
                                        #content_dic['media'] = '티스토리'
                                        content_dic['title'] = content['entryTitle']
                                        #content_dic['writer'] = '' # 이거때문에 화면 로딩해야 함 
                                        content_dic['date'] = content['entryPublished']
                                        #content_dic['content'] = ''
                                        content_dic['like'] = content['likeCount']
                                        content_dic['comment_count'] = content['commentCount']

                                        tstory_id_dic[content_url] = content_dic
                                    else:
                                        self.log.debug ('tstory_id_dic[url] exist: ' + content_url)
                                    
                        except Exception as e:
                            self.log.error ('error: ' + str(e))
                            self.log.error (traceback.print_exc())

                    if res_dic['data']['nextPage'] == 0:
                        break
                    
                    page += 1
                    url = url.split('&page=')[0]+'&page=' + str(page)
                
                    if is_finished:
                        break
            
            self.log.info ('keyword: "' + keyword + '", crawled_count: "' + str(len(tstory_id_dic) - previous_dic_count) + '"')
            previous_dic_count = len(tstory_id_dic)
        
        return tstory_id_dic
    
            
    def parse_tstory(self, response):
        
        item = TstorycrawlerItem()
        item['job_id'] = self.job_id
        item['url'] = response.url
        item['blog_id'] = response.meta['blog_id']
        
        entry_id = response.text.split('window.tiara =')[1].split('entryId":"')[1].split('"')[0]
        item['entry_id'] = entry_id
        
        item['keywords'] = response.meta['keywords']
        item['media'] = '티스토리'
        item['title'] = response.meta['title']
        item['writer'] = response.css('.by_blog ::text').get()
        item['date'] = response.meta['date']
        item['content'] = self.get_content(response)
        item['like'] = response.meta['like']
        item['comment'] = []
        
        if response.meta['comment_count'] > 0:       
            
            if 'entry' in response.url:
                comment_url = response.url.split('entry')[0] + 'api/' + entry_id + '/comment?'
            else: 
                comment_url = response.url.replace('/m/', '/m/api/') + '/comment?'
            #self.log.debug ('response.url: ' + response.url)
            #self.log.debug ('comment count: ' + str(response.meta['comment_count']) + ', url: ' + comment_url)
            item['comment'] = self.get_comment(comment_url)

        return item


    def get_content(self,response):
        contents = response.xpath('/html/body/div[1]/main/section/div/article/div[3]/text()').getall()     
        contents += response.xpath('/html/body/div[1]/main/section/div/article/div[3]/p[1]/span/text()').getall()
        contents += response.css('p ::text').getall()
        content_list = []
        for content in contents:
            content.replace('\n','')
            if content.strip() != '':
                content_list.append(content)
        return content_list
    

    def get_comment (self, url):
        comment_list = []
        
        try:
            response = requests.get(url)
            res_dic = json.loads(response.text)
            elements = res_dic['data']['items']
            
            for element in elements:
                '''
                {'id': 14191094, 'content': '좋은 정보 잘 보고, 공감하며, 광고도 보고 갑니다. 늘 행복하세요. ~~', 
                'written': '1시간 전', 'permalink': '', 'restrictType': None, 'isSecret': False, 'isPinned': False, 'parent': None, 'children': [], 
                'writer': {'id': 5445385, 'name': '송죽LJH1111', 'profileImage': 'https://tistory1.daumcdn.net/tistory/5438550/attach/5f24634c893c451aad491eaaddc829c9', 
                'homepage': 'https://jungtong.tistory.com', 'role': 'connected', 'canManage': False, 'isRequestUser': False}, 
                'mentionUserName': None, 'mentionId': None, 'supportId': None, 'type': 'NORMAL', 'orderAmount': None, 'supportStatus': None, 'profileLayer': []}
                '''
                try: 
                    comment = {}
                    comment['id'] = str(element['id'])
                    comment['nickname'] = element['writer']['name']
                    comment['date'] = self.to_date(element['written'])
                    comment['text'] = element['content'].replace('\n',' ')
                    if comment['nickname'] == '익명' and comment['text'] == '비밀댓글입니다.':
                        continue
                    else:
                        comment_list.append(comment)   
                except Exception as e:
                    self.log.error ('error: ' + str(e))
                    self.log.error (traceback.print_exc())
                    self.log.error (element)
                         
        except Exception as e:
            self.log.error ('error: ' + str(e))
            self.log.error (traceback.print_exc())

        return comment_list


    def init_mysql (self):
        self.conn = pymysql.connect(
            host = self.settings['MARIADB_HOST'],
            port = self.settings['MARIADB_PORT'],
            user = self.settings['MARIADB_USERNM'],
            password = self.settings['MARIADB_PASSWD'],
            db = self.settings['MARIADB_DBNM'], 
            charset = 'utf8')
        self.cur = self.conn.cursor()


    def to_date(self, str):
        temp = str.split('시간')
        day = temp[0].replace(' ','') 
        if len(temp) > 1:
            hour = int(day)
            time = datetime.now() - relativedelta(hours=(hour + 1))
        else:
            try:
                time = datetime.strptime(day, '%Y.%m.%d.%H:%M')
            except:
                time = datetime.now() - relativedelta(days=1)
                time.replace(hour=12, minute=0)
        return time.strftime('%Y-%m-%dT%H:%M:00+09:00')


    def random_sleep(self):
        time.sleep(self.secretsGenerator.uniform(1.0, 1.7))


    # def get_text_by_selector(self, selector):
    #     return self.driver.find_element(By.CSS_SELECTOR, selector).text
    
    def get_keyword(self):
        query_str = "SELECT topic, tstory_keyword, must_in_kr,must_co_kr,must_out_kr  FROM crawler_search_keyword ORDER BY num"
        self.log.debug ('query_string: ' + query_str)
        self.cur.execute(query_str)
        result = self.cur.fetchall()
        filtering_keyword = []       
        for res in result:
            search = {}
            search['topic'] = res[0]
            search['search_keyword'] = res[1].split(",")
            search['must_in_kr'] = res[2].split(",")
            search['must_co_kr'] = res[3].strip()
            search['must_out_kr'] = res[4].strip()
            filtering_keyword.append(search)
        return filtering_keyword

    def closed(self, reason):
        self.log.debug ('closed: ' + str(reason))
        cur_date = datetime.today()
        query_str = "UPDATE CRAWLER_STATUS SET status = 'C', crawler_end_date = '" + cur_date.strftime('%Y-%m-%d %H:%M:%S') + \
                "', update_date = '" + cur_date.strftime('%Y-%m-%d %H:%M:%S') + \
                "' where job_id = '{}' and sub_id = '{}'".format(self.job_id, self.sub_id)
        self.log.debug (query_str)
        result = self.cur.execute (query_str)
        if result == 0:
            result = self.cur.execute (query_str)
        self.log.debug ("update_result :"+str(result))
        self.conn.commit()


    def quit_self(self, reason):
        self.log.debug ('quit_self: ' + str(reason))
        sys.exit()
