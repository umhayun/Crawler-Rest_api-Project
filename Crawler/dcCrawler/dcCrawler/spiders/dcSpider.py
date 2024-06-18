import sys
import scrapy
from datetime import datetime, timedelta
from scrapy.utils.project import get_project_settings
import pymysql
import re
import math
import traceback
from dcCrawler.items import DccrawlerItem
from dateutil.relativedelta import relativedelta
from dcCrawler.log_util import LogUtil
import requests
from bs4 import BeautifulSoup 


class DcSpider(scrapy.Spider):
    name = 'dcSpider'
    headers = {'sec-fetch-mode' : 'cors', 
                'Connection' : 'keep-alive',
                'content-type' : 'application/x-www-form-urlencodedcharset=utf-8',
                'Accept-Language' : 'ko-KR,ko;q=0.9',
                'Referer':'https://www.dcinside.com/','accept': '*/*', 'sec-fetch-site': 'same-origin',
                'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}
    # 재난관련 갤러리
    galleries = ['accident2','typhoon1','earthquake','coronavirus','news_society'] # 사고, 태풍, 지진, 코로나, 범죄 
    # 재난관련 + 흥한갤
    # 사고, 태풍, 지진, 코로나, 범죄, 해외축구, 헬스, 국내야구, 남자 연예인, 해외야구, 메이플스토리, 비트코인, 기타 국내 드라마, 서울 미디어뉴스, 메디먼트뉴스
    top_galleries = ['accident2','typhoon1','earthquake','coronavirus','news_society','football_new8','extra_new1','baseball_new11','m_entertainer_new1','baseball_ab2','maplestory_new','bitcoins_new1','drama_new3','seoulmedianews','mmnews']
    test_list = ['m_entertainer_new1']
    url = 'https://m.dcinside.com/board/{}?page={}'


    def __init__(self, job_id='', sub_id='', *args, **kwargs):
        super(DcSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
         
        # 실행 정보 확인 
        # job_id는 한번에 실행되는 job의 단위, sub_id는 실행되는 crawler별로 생성
        self.job_id = job_id
        self.sub_id = sub_id 

        log_util = LogUtil('dcCrawler' + '-' + str(sub_id))
        self.log = log_util.get_logger()  # Scrapy에 logger가 정의되어 있어서 self.logger 사용 못함 

        self.init_mysql()

        # 검색 키워드
        self.filtering_keywords = self.get_keyword()

        # 검색 상세 조건
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
        

    def start_requests(self):
        for gall in self.top_galleries:
            dc_id_dic = self.get_list(gall)
            self.log.debug ('dc_id_dic: ' + str(len(dc_id_dic)))
            for url,data in dc_id_dic.items():
                yield scrapy.Request(url = url,callback = self.parse_dc,headers = self.headers,meta = data)


    def get_list(self,gall):
        self.start_page = math.ceil(self.start_index / 30) # 페이지당 30개
        self.end_page = math.ceil(self.end_index / 30)
        self.log.debug ('start_date: ' + str(self.start_date))
        self.log.debug ('end_date: ' + str(self.end_date))
        self.log.debug ('start_page: ' + str(self.start_page))
        self.log.debug ('end_page: ' + str(self.end_page))
        self.log.debug ('gallery id: ' + gall) 

        dc_id_dic = {}
        previous_dic_count = 0

        is_finished = False
        page = 1       
        while True:
            url = self.url.format(gall,page)
            self.log.debug ('search page: ' + url) #viewtop > div.gall-tit-box > span.count
            res = requests.get(url,headers=self.headers)
            soup = BeautifulSoup(res.text,"html.parser")
            lists = soup.select('.gall-detail-lst li .gall-detail-lnktb')  
            
            if soup.select_one('#viewtop > div.gall-tit-box > span'):
                count = int(soup.select_one('#viewtop > div.gall-tit-box > span').get_text().replace(',','').lstrip('(').rstrip(')'))     
                last_page = count//30
                for list in lists: 
                    try:
                        data = {}
                        post = list.select_one('a.lt')
                        post_date = post.select_one('.ginfo > li:nth-of-type(2)').get_text()
                        content_date = self.search_date(post_date)
                        
                        if content_date < self.start_date: # 검색 기간보다 전의 데이터 나오면 종료 
                            is_finished = True
                            self.log.debug ('content_date "' + str(content_date) + '" < start_date "' + str(self.start_date) + '"')
                            break
                        elif content_date > self.end_date: # 검색 기간보다 최근의 데이터 나오면 계속 확인  
                            self.log.debug ('content_date "' + str(content_date) + '" > end_date "' + str(self.end_date) + '"')
                            continue 
                        
                        # # 제목에 keyword 존재 확인                                        
                        content_title = post.select_one('.subjectin').get_text()
                        if self.job_type == 'M':
                            for keyword in self.keywords:
                                if keyword in content_title:
                                    post_url = post['href'].split('?')[0]
                                    if post_url not in dc_id_dic.keys():
                                        data['keyword'] = keyword 
                                        data['title'] = content_title
                                        dc_id_dic[post_url] = data
                        else:
                            for filtering in self.filtering_keywords:
                                for must_in_kr in filtering['must_in_kr']:
                                    # 필수키워드
                                    if must_in_kr not in content_title:
                                        continue                     
                                    # 제외키워드                      
                                    match_out_kr = re.match(filtering['must_out_kr'], content_title)
                                    if match_out_kr is not None:
                                        continue
                                    # 포함키워드
                                    match_co_kr = re.match(filtering['must_co_kr'], content_title)
                                    if match_co_kr is None:
                                        continue
                                    post_url = post['href'].split('?')[0]
                                    if post_url not in dc_id_dic.keys():
                                        data['keyword'] = must_in_kr 
                                        data['title'] = content_title
                                        print("title : ",content_title)
                                        dc_id_dic[post_url] = data
                        
                    except Exception as e:
                        self.log.error ('error: ' + str(e))
                        self.log.error (traceback.print_exc())
                self.log.info ("dic_length :"+str(len(dc_id_dic)))
                if page >= last_page:
                    break
                page += 1
                if is_finished:
                    break
            previous_dic_count = len(dc_id_dic)
        return dc_id_dic


    def parse_dc(self, response):
        try:
            item = DccrawlerItem()
            item['job_id'] = self.job_id
            item['url'] = response.url
            item['media'] = '디시인사이드'
            item['post_id'] = int(response.css('#no ::attr("value")').get())
            item['keywords'] = response.meta['keyword']
            item['title'] = response.meta['title']
            item['date'] = self.to_datetime(response.css('.gallview-tit-box .ginfo2 li:nth-of-type(2) ::text').get())
            item['writer'] = response.css('.btm .ginfo2 li ::text').get().split('(')[0]
            item['content'] = self.get_content(response)
            views = response.css('div.gall-thum-btm > div > ul > li:nth-of-type(1) ::text').get()
            item['views'] = int(views.split('조회수 ')[1])
            item['like'] = int(response.css('#recomm_btn ::text').get())
            item['dislike'] = int(response.css('#nonrecomm_btn ::text').get())

            # 댓글이 있는 것만 크롤링
            comment_count = response.css('.btn-commentgo .point-red ::text').get()
            if comment_count != '0':
                item['comment'] = self.get_comment(response)
            else:
                item['comment'] = []

        except Exception as e:
            self.log.error (response.url)
            self.log.error ('error: ' + str(e))
            self.log.error (traceback.print_exc())
        return item
    

    def get_content(self,response):
        contents = []
        contents += response.css('.thum-txt .thum-txtin p ::text').getall()
        content_div = response.css('.thum-txt .thum-txtin div').getall()
        for div in content_div:
            ad = BeautifulSoup(div,'html.parser')
            if ad.select_one('.adv-groupin') or ad.select_one('.adv-groupno') :
                continue
            else:
                if ad.select('div div'):
                    detail = ad.select('div div')
                    for d in detail:
                        contents.append(d.get_text())
                else: 
                    contents += ad.get_text().split('\n')
                    if '<br>' in ad.get_text():
                        contents += ad.get_text().split('<br>')

        contents = [v for v in contents if v] # 공백 제거   

        return list(set(contents))
 

    def get_comment(self,response):
        comment_list = []
        comments = response.css('.all-comment-lst li').getall()       
        for com in comments:
            comment = {}
            li = BeautifulSoup(com,'html.parser')
            try:
                comment['id'] = int(li.li['no'])
                comment['nickname'] = (li.select_one('.nick').get_text()).split('(')[0]
                comment['text'] = li.select_one('p.txt').get_text()
                comment['date'] = self.to_datetime(li.select_one('.date').get_text())
                if comment['text']:
                    comment_list.append(comment)
            except :
                continue
        return comment_list
    

    # 날짜 시간 변경
    def to_datetime(self, str):
        day = str.replace(' ','.') 

        year = datetime.now().date().strftime('%Y')       
        if len(day) <= 11:
            day = f'{year}.{day}'                
        time = datetime.strptime(day, '%Y.%m.%d.%H:%M') 
        return time.strftime('%Y-%m-%dT%H:%M:00+09:00')
    

    # 검색 날짜형식으로 변경
    def search_date(self,post_date):
        year = datetime.now().date().strftime('%Y') 
        strdate = datetime.now()
        if ":" in post_date:
            today = datetime.now().date().strftime('%Y-%m-%d') 
            strdate = f'{today} {post_date}:00'
        elif len(post_date) <= 5:
            post_date = post_date.replace('.','-')
            strdate = f'{year}-{post_date} 00:00:00' 
        else:
            post_date = post_date.replace('.','-')
            strdate = f'20{post_date} 00:00:00'

        return datetime.strptime(strdate,'%Y-%m-%d %H:%M:00')
    

    # 조회수 숫자 형식으로 변환
    def to_number(self,views):
        if '만' in views:
            num = views.split('만')[0]
            float(num.strip())*10000
        else:
            num = views.replace(',', '')
        return int(num)
    
    def init_mysql (self):
        self.conn = pymysql.connect(
            host = self.settings['MARIADB_HOST'],
            port = self.settings['MARIADB_PORT'],
            user = self.settings['MARIADB_USERNM'],
            password = self.settings['MARIADB_PASSWD'],
            db = self.settings['MARIADB_DBNM'], 
            charset = 'utf8')
        self.cur = self.conn.cursor()

    def get_keyword(self):
        query_str = "SELECT topic, must_in_kr,must_co_kr,must_out_kr  FROM crawler_search_keyword ORDER BY num"
        self.log.debug ('query_string: ' + query_str)
        self.cur.execute(query_str)
        result = self.cur.fetchall()
        filtering_keyword = []       
        for res in result:
            search = {}
            search['topic'] = res[0]
            search['must_in_kr'] = res[1].split(",")
            search['must_co_kr'] = res[2].strip()
            search['must_out_kr'] = res[3].strip()
            filtering_keyword.append(search)
        return filtering_keyword
    
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