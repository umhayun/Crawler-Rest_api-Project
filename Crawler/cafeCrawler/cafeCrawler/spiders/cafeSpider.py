import sys
import scrapy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from scrapy.utils.project import get_project_settings
from selenium.webdriver.common.by import By
import secrets
import time
import pymysql
import math
import traceback
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from cafeCrawler.items import CafecrawlerItem
from fake_useragent import UserAgent
from cafeCrawler.log_util import LogUtil



class CafeSpider(scrapy.Spider):

    name = 'cafeSpider'
    search_cafe = "https://section.cafe.naver.com/ca-fe/home/search/articles?q={}&pr=7&em=1&od=1&p=1"
    headers = {'sec-fetch-mode': 'cors', 'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
               'accept': '*/*', 'sec-fetch-site': 'same-origin'}

    def __init__(self, job_id='', sub_id='', *args, **kwargs):
        super(CafeSpider, self).__init__(*args, **kwargs)

        self.settings = get_project_settings()
         
        # 실행 정보 확인 
        # job_id는 한번에 실행되는 job의 단위, sub_id는 실행되는 crawler별로 생성
        self.job_id = job_id
        self.sub_id = sub_id 
   
        log_util = LogUtil('naverCafeCrawler' + '-' + str(sub_id))
        self.log = log_util.get_logger()  # Scrapy에 logger가 정의되어 있어서 self.logger 사용 못함 
        
        self.init_driver()
        self.init_mysql()
        self.url_dic = dict() # 중복 체크용 

        # 검색 keyword 출력
        self.filtering_keywords = self.get_keyword()
        # 상세 검색조건 
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
        yield scrapy.Request(url=self.search_cafe, callback=self.parse_search_result, headers=self.headers)


    def parse_search_result (self,response):
        self.start_page = math.ceil(self.start_index / 12)
        self.end_page = math.ceil(self.end_index / 12) 
        self.log.debug ('start_date: ' + str(self.start_date))
        self.log.debug ('end_date: ' + str(self.end_date))
        self.log.debug ('start_page: ' + str(self.start_page))
        self.log.debug ('end_page: ' + str(self.end_page))
        manual_num = 0
        # while self.start_date.strftime('%Y-%m-%d') <= self.end_date.strftime('%Y-%m-%d'):
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
                if '&' in keyword:
                    keyword = keyword.replace('&',"%26") 
                cafe_url = self.search_cafe.format(keyword)
                cafe_id_dic = self.get_cafe_list(cafe_url, filtering,keyword)
                
                for key,value in cafe_id_dic.items():
                    yield self.parse_cafe(key,value)
                    
            #self.start_date += relativedelta(days=1)


    def get_cafe_list(self, cafe_list_url, filtering, keyword):
        is_finished = False
        cafe_id_dic = dict()
        self.log.debug ('cafe_list_url: ' + cafe_list_url)
        self.driver.get(cafe_list_url)
        self.random_short_sleep()
            
        # 크롤링 시작 페이지와 끝 페이지 계산
        try:
            total = self.get_text_by_selector('.sub_text')
            last_page = int(total.replace(',', '')) // 12
            self.log.debug ('content_count: ' + str(total))
            self.log.debug ('last_page: ' + str(last_page))
                
            if self.start_page > last_page: 
                return cafe_id_dic
            if self.start_page > 100: 
                return cafe_id_dic
        except Exception as e:
            self.log.error ('get last_page error: ' + str(e))
            self.log.error (traceback.print_exc())
            return cafe_id_dic
        
        end_page = min (last_page, self.end_page, 100) 
        self.log.debug ('end_page = ' + str(end_page))

        for i in range(self.start_page, end_page + 1):
            try:                            
                cafe_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.item_list  .ArticleItem ')
                for element in cafe_elements:
                    url = element.find_element(By.CSS_SELECTOR,'.article_item_wrap > a ').get_attribute('href')
                    title = element.find_element(By.CSS_SELECTOR,'.article_item_wrap > a .title').text
                    date = element.find_element(By.CSS_SELECTOR,'.cafe_info .date').text      
                    content_date = self.to_datetime(date)   

                    if content_date < self.start_date: # 검색 기간보다 전의 데이터 나오면 종료 
                        is_finished = True
                        self.log.debug ('content_date "' + str(content_date) + '" < start_date "' + str(self.start_date) + '"')
                        break
                    elif content_date > self.end_date: # 검색 기간보다 최근의 데이터 나오면 계속 확인  
                        self.log.debug ('content_date "' + str(content_date) + '" > start_date "' + str(self.end_date) + '"')
                        continue 

                    # if keyword not in title:
                    #     self.log.debug ('keyword "' + keyword + '" is not in "' + title + '"')
                    #     continue
                    if self.job_type == "M":
                        if keyword in title:
                            value = self.url_dic.get(url.split('?')[0])
                            if value == None: 
                                self.url_dic[url.split('?')[0]] = 'value'    # 미정 
                                keyword_list = cafe_id_dic.get(url)          
                                if keyword_list == None:
                                    cafe_id_dic[url] = [keyword]
                                else:
                                    keyword_list.append(keyword)
                                    cafe_id_dic[url] = list(set(keyword_list))
                            else: 
                                self.log.debug ('url exist: ' + url.split('?')[0])
                    else:
                        for must_in_kr in filtering['must_in_kr']:
                            # 필수키워드
                            if must_in_kr not in title:
                                continue                     
                            # 제외키워드                      
                            match_out_kr = re.match(filtering['must_out_kr'], title)
                            if match_out_kr is not None:
                                continue
                            # 포함키워드
                            match_co_kr = re.match(filtering['must_co_kr'], title)
                            if match_co_kr is None:
                                continue
                            self.log.debug ('title: ' +title)
                            # 여러 키워드를 저장하는 구조가 아니라서 그냥 바로 dic에 설정만 함. 
                            # 중복 체크는 별도의 dic 사용 
                            value = self.url_dic.get(url.split('?')[0])
                            if value == None: 
                                self.url_dic[url.split('?')[0]] = 'value'    # 미정 
                                keyword_list = cafe_id_dic.get(url)          
                                if keyword_list == None:
                                    cafe_id_dic[url] = [must_in_kr]
                                else:
                                    keyword_list.append(must_in_kr)
                                    cafe_id_dic[url] = list(set(keyword_list))
                            else: 
                                self.log.debug ('url exist: ' + url.split('?')[0])

                self.log.debug ('cafe_id_dic count: ' + str(len(cafe_id_dic)))
                
                if i >= 100: #하나의 검색어에 대해 100페이지까지만 검색됨
                    break
                if is_finished:
                    break

                cafe_list_url = cafe_list_url.split('&p=')[0] + '&p=' + str(i+1)
                self.driver.get(cafe_list_url)
                self.log.debug ('cafe_list_url: ' + cafe_list_url)
                self.random_short_sleep()

            except Exception as e:
                self.log.error ('error: ' + str(e))
                self.log.error (traceback.print_exc())
                cafe_list_url = cafe_list_url.split('&p=')[0] + '&p=' + str(i+1)
                self.driver.get(cafe_list_url)
                self.log.error (cafe_list_url)
                self.random_short_sleep()


        self.log.debug ('total blog_id_dic count:' + str(len(cafe_id_dic))) 
        return cafe_id_dic
    
    
    def parse_cafe(self, url, keyword):
        self.driver.get(url)
        self.random_sleep()
        item = CafecrawlerItem()
        item['job_id'] = self.job_id
        try: 
            self.driver.switch_to.frame('cafe_main')
        except Exception as e:
            self.log.error ('cafe_main error: ' + str(e))
            self.log.error ('url: ' + url)
            self.log.error (traceback.print_exc())
            return item

        try:
            item['media'] = '네이버_카페'
            item['keywords'] = keyword
            try: 
                item['title'] = self.get_text_by_selector('.article_wrap .title_text')
            except Exception as e:
                self.log.error ('error: ' + str(e))
                self.log.error (traceback.print_exc())
                item['title'] = ''
                
            item['real_url'] = url
            item['url'] = self.driver.find_element(By.CSS_SELECTOR,"#spiButton").get_attribute('data-url')
            
            item['date'] = self.to_date(self.get_text_by_selector('.date'))
            item['views'] = self.to_number(self.get_text_by_selector('.article_info .count').split('조회 ')[1])
            item['writer'] = self.get_text_by_selector('.nickname')

            contents = self.driver.find_elements(
                By.CSS_SELECTOR, '.se-component-content span')
            item['content'] = self.content_list(contents)

            try:
                item['comment'] = self.parse_comment()
            except:
                item['comment'] = []

            try:
                item['like'] = self.to_number(self.get_text_by_selector('em.u_cnt._count'))
            except:
                
                item['like'] = 0
        except Exception as e:
            self.log.error ('error: ' + str(e))
            self.log.error (traceback.print_exc())
            self.log.error ('url: ' + url)

        return item

    def parse_comment(self):
        comment_list = []
        try:
            comments = self.driver.find_elements(By.CSS_SELECTOR, '.CommentItem')
            for i in comments:
                comment = {}
                if i.find_element(By.CSS_SELECTOR, ' .text_comment').text != '':
                    comment['id'] = str(i.get_attribute('id'))
                    comment['nickname'] = i.find_element(By.CSS_SELECTOR, '.comment_nickname').text
                    comment['text'] = i.find_element(By.CSS_SELECTOR, ' .text_comment').text.replace('\n',' ')
                    comment['date'] = self.to_date(i.find_element(By.CSS_SELECTOR, ' .comment_info_date').text)
                    comment_list.append(comment)
                    
        except:
            pass
        return comment_list

    def content_list(self, contents):
        content = []
        for c in contents:
            if c.text.strip() == '' or c.text.strip() == '\u200b':
                continue
            content.append(c.text)
        return content

    def init_driver(self):
        ua = UserAgent()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('user-agent=' + ua.random)
        chrome_options.add_argument('--lang=ko')
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-extensions")       
        chrome_options.add_argument("--noconsole")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches',['enable-logging'])
        service=Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service,options=chrome_options)
        self.driver = driver


    def init_mysql (self):
        self.conn = pymysql.connect(
            host = self.settings['MARIADB_HOST'],
            port = self.settings['MARIADB_PORT'],
            user = self.settings['MARIADB_USERNM'],
            password = self.settings['MARIADB_PASSWD'],
            db = self.settings['MARIADB_DBNM'], 
            charset = 'utf8')
        self.cur = self.conn.cursor()


    # 날짜 시간 변경 
    def to_date(self, date):
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')
        if '분' in date:
            min = int(date.split('분')[0])
            time = datetime.now() - relativedelta(minutes=(min + 1))
        elif '초' in date:
            sec = int(date.split('초')[0])
            time = datetime.now() - relativedelta(seconds=(sec + 1))
        elif '시간' in date:
            hour = int(date.split('시간')[0])
            time = datetime.now() - relativedelta(hours=(hour + 1))
        else:
            time = datetime.strptime(date, '%Y.%m.%d. %H:%M')
        str_date = time.strftime('%Y-%m-%dT%H:%M:%S+09:00')

        return str_date

    # 조회수 숫자 형식으로 변환
    def to_number(self,views):
        if '만' in views:
            num = views.split('만')[0]
            float(num.strip())*10000
        else:
            num = views.replace(',', '')
        return int(num)


    def random_sleep(self):
        time.sleep(self.secretsGenerator.uniform(1.5, 2.0)) # cafe 게시글 로딩이 오래 걸림 


    def random_short_sleep(self):
        time.sleep(self.secretsGenerator.uniform(0.6, 0.8))


    def get_text_by_selector(self, selector):
        return self.driver.find_element(By.CSS_SELECTOR, selector).text
    
    def get_keyword(self):
        query_str = "SELECT topic, cafe_keyword,must_in_kr,must_co_kr,must_out_kr  FROM crawler_search_keyword  ORDER BY num"
        self.cur.execute(query_str)
        result = self.cur.fetchall()
        filtering_keyword = []       
        for res in result:
            search = {}
            search['topic'] = res[0]
            search['search_keyword'] = res[1].split(",")
            search['must_in_kr'] = res[2].split(",")
            search['must_co_kr'] = res[3].replace(",","|")
            search['must_out_kr'] = res[4].replace(",","|")
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
        self.log.debug ("update_result :"+str(result))
        self.conn.commit ()

        self.driver.close()
        self.driver.quit()


    def quit_self(self, reason):
        self.log.debug ('quit_self: ' + str(reason))
        self.driver.close()
        self.driver.quit()
        sys.exit()
    
    
    def to_datetime(self, str):         
        if '전' in str:
            if '분' in str:
                min = int(str.split('분')[0])
                time = datetime.now() - relativedelta(minutes=(min + 1))
            else:
                hour = int(str.split('시')[0])
                time = datetime.now() - relativedelta(hours=(hour + 1))            
        else:
            time = datetime.strptime(str, '%Y.%m.%d.') 
        strdate = time.strftime('%Y-%m-%dT%H:%M:%S+09:00')
        return datetime.strptime(strdate,'%Y-%m-%dT%H:%M:%S+09:00')
