import sys
import scrapy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from scrapy.utils.project import get_project_settings
import secrets
import time
import pymysql
import math
import traceback
from fmCrawler.log_util import LogUtil
from fmCrawler.items import FmcrawlerItem

import requests
from bs4 import BeautifulSoup 


class FmSpider(scrapy.Spider):
    name='fmSpider'
    url='https://www.fmkorea.com/search.php?act=IS&is_keyword={}&mid=home&where=document&search_target=title&page={}'

    def __init__(self, job_id='', sub_id='', *args, **kwargs):
        super(FmSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
        
        # 실행 정보 확인 
        # job_id는 한번에 실행되는 job의 단위, sub_id는 실행되는 crawler별로 생성
        self.job_id = job_id
        self.sub_id = sub_id 

        log_util = LogUtil('fmCrawler' + '-' + str(sub_id))
        self.log = log_util.get_logger()  # Scrapy에 logger가 정의되어 있어서 self.logger 사용 못함 

        self.init_mysql()

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
        fm_id_dic = self.get_list()
        self.log.debug ('fm_id_dic: ' + str(len(fm_id_dic)))
        for url,data in fm_id_dic.items():
            yield scrapy.Request(url=url,callback=self.parse_fm, meta=data)


    def get_list(self):
        # 10개씩 1000페이지 => 10000개 
        # self.start_page = math.ceil(self.start_index / 30) # 페이지당 30개
        # self.end_page = math.ceil(self.end_index / 30)
        self.log.debug ('start_date: ' + str(self.start_date))
        self.log.debug ('end_date: ' + str(self.end_date))
        fm_id_dic = {}
        try:
            for keyword in self.keywords:
                self.log.debug ('keyword: "' + keyword + '" started')

                is_finished = False
                for page in range(1,1001):
                    res = requests.get(self.url.format(keyword,page))                                                                                 
                    source = BeautifulSoup(res.text,'html.parser')
                    lists = source.select('.searchResult li')
                    
                    for list in lists:
                        data = {}
                        href = list.select_one('a')['href']
                        post_url = 'https://www.fmkorea.com' + href
                        title = list.select_one('a').get_text().split(']',maxsplit=1)[1].strip()
                        info = list.select_one('address span.time').get_text()
                        date = self.to_datetime(info)
                        content_date = datetime.strptime(date,'%Y-%m-%dT%H:%M:%S+09:00')

                        if content_date < self.start_date: # 검색 기간보다 전의 데이터 나오면 종료 
                            is_finished = True
                            self.log.debug ('content_date "' + str(content_date) + '" < start_date "' + str(self.start_date) + '"')
                            break
                        elif content_date > self.end_date: # 검색 기간보다 최근의 데이터 나오면 계속 확인  
                            self.log.debug ('content_date "' + str(content_date) + '" > end_date "' + str(self.end_date) + '"')
                            continue 

                        data['title'] = title
                        data['writer'] = info[0].strip()
                        data['date'] = date
                        fm_id_dic[post_url] = data 

                    if is_finished:
                        break
                self.log.debug ('keyword: ' + keyword + ' end')
                self.log.debug ('fm_id_dic: ' +str(len(fm_id_dic)))

        except Exception as e:
            self.log.error(res.url)
            self.log.error ('error: ' + str(e))
            self.log.error (traceback.print_exc())
                                         
        return fm_id_dic
    
    
    def parse_fm(self,response):
        item = FmcrawlerItem()
        item['url'] = response.url
        item['media'] = '에프엠코리아'
        item['title'] = response.meta['title']
        item['writer'] = response.meta['writer']
        item['date'] = response.meta['date']
        item['post_id'] = int(response.css('.scrap_layer input[name="document_srl"] ::attr(value)').get())
        item['views'] = int(response.css('.btm_area div.side.fr span:nth-child(1) b ::text').get())
        item['like'] = int(response.css('.btm_area div.side.fr span:nth-child(2) b ::text').get())
        item['content'] = self.get_content(response)
        comment_cnt = int(response.css('.btm_area div.side.fr span:nth-child(3) b ::text').get())
        item['comment'] = []
        if comment_cnt != 0:
            item['comment'] = self.get_comment(item['post_id'],comment_cnt)
        
        return item
    
    
    def get_content(self,response):
        contents = response.css('.rd_body article .xe_content').get()
        con_div = BeautifulSoup(contents,'html.parser')
        content_list = []     
        c_tags = []    
        if con_div.find('p'):
            c_tags.extend(con_div.find_all('p'))
        elif con_div.div.find('div'):           
            c_tags.extend(con_div.div.find_all('div'))
        else:
            content_list.append(con_div.div.get_text())
        for tag in c_tags:       
            if tag.select_one('.auto_media') or tag.find('video'):
                continue
            if tag.get_text() != '':
                content_list.append(tag.get_text())
            
        return content_list


    def get_comment(self,post_id,comment_cnt):
        page = 1 

        comment_list = []
        while True:
            comment_url = f'https://www.fmkorea.com/index.php?document_srl={post_id}&cpage={page}#{post_id}_comment'
            res = requests.get(comment_url)
            html = BeautifulSoup(res.text,'html.parser')             
            comments = html.select(f'.fdb_lst_wrp .fdb_lst_ul li')
            for com in comments:
                comment = {}
                comment['id'] = com['id'].split('_')[1]
                comment['nickname'] = com.select_one('.member_plate').get_text()
                # 댓글 분류
                com_div = com.select_one('.comment-content')
                if '삭제된 댓글' in com_div.get_text():
                    comment_cnt -= 1
                    continue      
                if com.select_one('.findComment'):
                    continue      
                if com_div.find('a'):
                    parent_nick = com_div.find('a').get_text().strip()
                    c_text = com_div.get_text().strip()              
                    text_list = c_text.strip(parent_nick).split('\n')
                else:
                    text_list = com_div.get_text().split('\n')
                comment['text'] = text_list
                comment['date'] = self.to_datetime(com.select_one('.date').get_text())
                
                comment_list.append(comment)
            page += 1
            if len(comment_list) >= comment_cnt:
                break
            
        return comment_list 


    # 날짜 시간 변경
    def to_datetime(self, str):        
        if '전' in str:
            if '분' in str:
                min = int(str.split(' ')[0])
                time = datetime.now() - relativedelta(minutes=(min + 1))
            else:
                hour = int(str.split(' ')[0])
                time = datetime.now() - relativedelta(hours=(hour + 1))            
        else:
            str = str.replace('.','-')     
            time = datetime.strptime(str, '%Y-%m-%d %H:%M') 
        str_date = time.strftime('%Y-%m-%dT%H:%M:%S+09:00')
        return str_date

    
    def init_mysql (self):
        self.conn = pymysql.connect(
            host = self.settings['MARIADB_HOST'],
            port = self.settings['MARIADB_PORT'],
            user = self.settings['MARIADB_USERNM'],
            password = self.settings['MARIADB_PASSWD'],
            db = self.settings['MARIADB_DBNM'], 
            charset = 'utf8')
        self.cur = self.conn.cursor()


    def quit_self(self, reason):
        self.log.debug ('quit_self: ' + str(reason))
        sys.exit()


    def closed(self, reason):
        self.log.debug ('closed: ' + str(reason))
        cur_date = datetime.today()
        query_str = "UPDATE CRAWLER_STATUS SET status = 'C', crawler_end_date = '" + cur_date.strftime('%Y-%m-%d %H:%M:%S') + \
                "', update_date = '" + cur_date.strftime('%Y-%m-%d %H:%M:%S') + \
                "' where job_id = '{}' and sub_id = '{}'".format(self.job_id, self.sub_id)
        self.log.debug (query_str)
        self.cur.execute (query_str)
        self.conn.commit ()