import sys
import scrapy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from scrapy.utils.project import get_project_settings
import secrets
import time
import pymysql
import re
import math
import traceback
from ppomppuCrawler.items import PpomppuCrawlerItem
from ppomppuCrawler.log_util import LogUtil
import requests
from bs4 import BeautifulSoup 

class PpomppuSpider(scrapy.Spider):
    name = 'ppomppuSpider'
    url = 'https://www.ppomppu.co.kr/search_bbs.php?page_size=50&bbs_cate=2&keyword={}&order_type=date&search_type=sub_memo&search_type=subject&page_no={}'
    
    def __init__(self, job_id='', sub_id='', *args, **kwargs):
        super(PpomppuSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
         
        # 실행 정보 확인 
        # job_id는 한번에 실행되는 job의 단위, sub_id는 실행되는 crawler별로 생성
        self.job_id = job_id
        self.sub_id = sub_id 

        log_util = LogUtil('ppomppuCrawler' + '-' + str(sub_id))
        self.log = log_util.get_logger()  # Scrapy에 logger가 정의되어 있어서 self.logger 사용 못함 

        self.init_mysql()
        # 연산 키워드 
        self.filtering_keywords = self.get_keyword()
        # 검색 상세조건
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
        ppomppu_id_dic = self.get_list()
        self.log.debug ('ppomppu_id_dic: ' + str(len(ppomppu_id_dic)))
        for url,data in ppomppu_id_dic.items():
            yield scrapy.Request(url=url,callback=self.parse_ppomppu,meta=data)


    def get_list(self):
        # self.start_page = math.ceil(self.start_index / 30) # 페이지당 30개
        # self.end_page = math.ceil(self.end_index / 30)
        self.log.debug ('start_date: ' + str(self.start_date))
        self.log.debug ('end_date: ' + str(self.end_date))
        # self.log.debug ('start_page: ' + str(self.start_page))
        # self.log.debug ('end_page: ' + str(self.end_page))
        manual_num = 0
        ppomppu_id_dic = {}   
        previous_dic_count = 0   
        for filtering in self.filtering_keywords:
            if self.job_type == "M":
                manual_num += 1
                if manual_num > 1:
                    break     
                filtering['search_keyword'] = self.keywords
                self.log.debug ('topic: ' + str(filtering['search_keyword']))
            else:
                self.log.debug ('topic: ' + filtering['topic'])
            for keyword in filtering['search_keyword']:
                is_finished = False
                page = 1
                while True:
                    url = self.url.format(keyword,page)
                    res = requests.get(url)
                    source = BeautifulSoup(res.content,'html.parser')
                    last_page = source.select_one('.results_board > p')
                    lists = source.select('.results_board .conts .content') 
                    if len(lists) == 0:
                        break
                    for list in lists:
                        try:
                            if list.select_one('.title').find('a'):
                                data = {}
                                content_date = list.select_one('.desc > span:nth-child(3)').get_text().replace('.','-')+" 00:00:00"

                                content_date = datetime.strptime(content_date, '%Y-%m-%d 00:00:00') 

                                if content_date < self.start_date: # 검색 기간보다 전의 데이터 나오면 종료 
                                    is_finished = True
                                    self.log.debug ('content_date "' + str(content_date) + '" < start_date "' + str(self.start_date) + '"')
                                    break
                                elif content_date > self.end_date: # 검색 기간보다 최근의 데이터 나오면 계속 확인  
                                    self.log.debug ('content_date "' + str(content_date) + '" > end_date "' + str(self.end_date) + '"')
                                    continue   
                                title = list.select_one('.title a').get_text()
                                must_keyword = ''
                                href = ''
                                if self.job_type == "M":
                                    if keyword in title:
                                        href = list.select_one('.title a')['href']                             
                                        post_url = 'https://www.ppomppu.co.kr' + href
                                        no = href.split('&')[1]
                                        dic = [k for k in ppomppu_id_dic.keys() if no in k]  
                                        if len(dic) == 0:
                                            title = list.select_one('.title a').get_text()
                                            cnt = list.select_one('.title .comment-cnt').get_text()
                                            data['title'] = title.rstrip(cnt)                         
                                            data['comment_cnt'] = int(cnt)
                                            data['views'] = list.select_one('.desc span:nth-child(2)').get_text().split(':')[1].strip()
                                            data['like'] = list.select_one('.desc .like').get_text().strip()
                                            data['dislike'] = list.select_one('.desc .dislike').get_text().strip()
                                            data['keyword'] = must_keyword
                                            ppomppu_id_dic[post_url] = data
                                        else:
                                            self.log.debug('duplicated post')   
                                else:
                                    for must_in_kr in filtering['must_in_kr']:
                                        # 필수키워드
                                        if must_in_kr not in title:
                                            continue
                                        else :
                                            must_keyword = must_in_kr                     
                                        # 제외키워드                      
                                        match_out_kr = re.match(filtering['must_out_kr'], title)
                                        if match_out_kr is not None:
                                            continue
                                        # 포함키워드
                                        match_co_kr = re.match(filtering['must_co_kr'], title)
                                        if match_co_kr is None:
                                            continue
                                        href = list.select_one('.title a')['href']                             
                                        post_url = 'https://www.ppomppu.co.kr' + href
                                        no = href.split('&')[1]
                                        dic = [k for k in ppomppu_id_dic.keys() if no in k]  
                                        if len(dic) == 0:
                                            title = list.select_one('.title a').get_text()
                                            cnt = list.select_one('.title .comment-cnt').get_text()
                                            data['title'] = title.rstrip(cnt)                         
                                            data['comment_cnt'] = int(cnt)
                                            data['views'] = list.select_one('.desc span:nth-child(2)').get_text().split(':')[1].strip()
                                            data['like'] = list.select_one('.desc .like').get_text().strip()
                                            data['dislike'] = list.select_one('.desc .dislike').get_text().strip()
                                            data['keyword'] = must_keyword
                                            ppomppu_id_dic[post_url] = data
                                        else:
                                            self.log.debug('duplicated post')                       

                        except Exception as e:
                            self.log.error(url)
                            self.log.error ('error: ' + str(e))
                            self.log.error (traceback.print_exc())
                                         
                    page += 1

                    if is_finished:
                        break

                    if last_page!=None:
                        break

            self.log.info (' crawled_count: "' + str(len(ppomppu_id_dic) - previous_dic_count) + '"')
            previous_dic_count = len(ppomppu_id_dic)
            
        return ppomppu_id_dic

    def parse_ppomppu(self,response):
        try:
            item = PpomppuCrawlerItem()
            item['job_id'] = self.job_id
            item['media'] = '뽐뿌'
            item['url'] = response.url
            item['title'] = response.meta['title']
            try:
                item['post_id'] = response.css('#copyTarget ::attr(value)').get().split('&no=')[1]
            except:
                item['post_id'] = 'anonymous'
            info_tag = response.css('.sub-top-contents-box .sub-top-text-box').get()
            post_date = info_tag.split('등록일: ')[1].split('\r\n')[0]
            item['date'] = self.to_datetime(post_date.replace('<br>',''))
            item['keyword'] = response.meta['keyword']
            # 닉네임 이미지인 경우 구분   
            nick = response.css('.view_name ::text').get()
            if nick == None:
                nick = response.css('div.sub-top-text-box > span:nth-child(5) > a > img ::attr(alt)').get()
                if nick == None:
                    nick = '익명'
            item['writer'] = nick
            item['like'] = int(response.meta['like'])
            item['dislike'] = int(response.meta['dislike'])
            item['views'] = int(response.meta['views'])
            item['content'] = self.get_content(response)
            item['comment']=[]
            if response.meta['comment_cnt'] !=0:
                item['comment'] = self.get_comment(response)

        except Exception as e:
            self.log.error(response.url)
            self.log.error ('error: ' + str(e))
            self.log.error (traceback.print_exc())
        return item
    
    
    def get_content(self,response):
        content = []
        content_tag = response.css('.board-contents').get()
        source = BeautifulSoup(content_tag,'html.parser')
        p_tag = source.find_all('p')
        for p in p_tag:
            if p.find('iframe') or p.find('video') :
                continue
            if p.get_text(strip=True) != '':
                content = p.get_text(strip=True)
        return content
    
    def get_comment(self,response):
        source = BeautifulSoup(response.text,'html.parser')
        comments = source.select('#newbbs #quote .comment_line')
        comment_list = []
        for com in comments:
            comment = {}
            comment_id = com.select_one('a')['id']
            texts = com.select_one(f'#commentContent_{comment_id}').get_text().split('\n')    
            com_text = []
            # 공백제거  
            for t in texts:
                new = t.strip()

                if new != '':
                    com_text.append(new)
                
            # 닉네임 이미지인 경우 구분   
            nick_tag = com.find('b')          
            nick = nick_tag.get_text()
            if nick == '':
                nick = nick_tag.find('img')['alt']  

            # 당일 댓글일 경우 구분
            date_tag = com.select_one('.eng-day')
            date = date_tag['title'][:16].strip()
            if date == '':
                today = datetime.now().strftime('%Y-%m-%d')
                time = date_tag.get_text()[:5]
                date = f"{today} {time}"

            comment['id'] = comment_id
            comment['text'] = com_text
            comment['nickname'] = nick
            comment['date'] = self.to_datetime(date)
            comment['like'] = int(com.select_one(f'#vote_cnt_{comment_id}').get_text())
            try:
                comment['dislike'] = int(com.select_one(f'#anti_vote_cnt_{comment_id}').get_text())
            except:
                comment['dislike'] = 0

            if comment['text']:
                comment_list.append(comment)

        return comment_list

    
    # 날짜 시간 변경
    def to_datetime(self, str):               
        time = datetime.strptime(str, '%Y-%m-%d %H:%M') 
        return time.strftime('%Y-%m-%dT%H:%M:00+09:00')
    
    def random_short_sleep(self):
        time.sleep(self.secretsGenerator.uniform(0.3, 1.4))
    
    def get_keyword(self):
        query_str = "SELECT topic, ppomppu_keyword, must_in_kr,must_co_kr,must_out_kr  FROM crawler_search_keyword ORDER BY num"
        self.log.debug ('query_string: ' + query_str)
        self.cur.execute(query_str)
        result = self.cur.fetchall()
        filtering_keyword = []       
        for res in result:
            search = {}
            search['topic'] = res[0]
            search['search_keyword'] = res[1].split(",")
            search['must_in_kr'] = res[2].split(",")
            search['must_co_kr'] = res[3]
            search['must_out_kr'] = res[4]
            filtering_keyword.append(search)
        return filtering_keyword
    
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
        result = self.cur.execute (query_str)
        if result == 0:
            result = self.cur.execute (query_str)
        self.log.debug ("update_result :"+str(result))
        self.conn.commit ()

    def quit_self(self, reason):
        self.log.debug ('quit_self: ' + str(reason))
        sys.exit()

