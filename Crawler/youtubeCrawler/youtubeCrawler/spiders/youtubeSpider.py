# -*- coding: utf-8 -*-

from random import uniform
import sys
import traceback
from dateutil.relativedelta import relativedelta
import pymysql
import scrapy
from youtubeCrawler.log_util import LogUtil
from youtubeCrawler.items import YoutubeCrawlerItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import re, time
from fake_useragent import UserAgent
from scrapy.utils.project import get_project_settings
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import secrets
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import html
from webdriver_manager.chrome import ChromeDriverManager


class YoutubeSpider(scrapy.Spider):
    name = 'youtubeSpider'
    # 향후 DB 연동으로 갈지 검토 필요 
    #keywords = ['사고'] 
    youtube_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15',
    }

    def __init__(self, job_id='', sub_id='', *args, **kwargs):
        super(YoutubeSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
         # 실행 정보 확인 
        # job_id는 한번에 실행되는 job의 단위, sub_id는 실행되는 crawler별로 생성
        self.job_id = job_id
        self.sub_id = sub_id 
        
        self.init_driver()
        log_util = LogUtil('youtubeCrawler' + '-' + str(1))
        self.log = log_util.get_logger()  # Scrapy에 logger가 정의되어 있어서 self.logger 사용 못함 

        self.init_mysql()
        # 검색 키워드
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
                if cursor[7] != None:   
                    self.period = int(cursor[7])
                else:
                    self.period = 0
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
                #start_date_str = '2023-10-19 00:00:00'
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
        yield scrapy.Request(url='https://www.youtube.com/', callback=self.get_search_result, headers = self.youtube_headers, errback=self.error_page)


    def get_search_result(self, response):
        self.log.debug ('start_date: ' + str(self.start_date))
        self.log.debug ('end_date: ' + str(self.end_date))
        # 검색 결과 크롤링
        manual_num = 0
        youtube_id_dic = {}
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
                after = self.start_date.strftime("%Y-%m-%d")
                before = self.end_date.strftime("%Y-%m-%d")
                period_query = f"{keyword} before:{before} after:{after}"
                self.driver.get(f'https://www.youtube.com/results?search_query={period_query}&sp=CAI')
                self.random_sleep()
                url_list = []
                try:
                    self.driver.find_element(By.CSS_SELECTOR,".promo-title")
                    continue
                except:
                    pass

                self.go_bottom(self.driver)

                video_list_page = self.driver.find_element(By.CSS_SELECTOR, '#contents')       
                video_elements = video_list_page.find_elements(By.CSS_SELECTOR,'.text-wrapper')

                self.log.debug ('search keyword: ' + keyword)
                self.log.debug ('search result count: ' + str(len(video_elements)))

                for video_element in video_elements:
                    data = {}
                    try:                 
                        ref_url = video_element.find_element(By.CSS_SELECTOR,'a#video-title').get_attribute('href')
                        title = video_element.find_element(By.CSS_SELECTOR,'a#video-title').get_attribute('title')
                        if (ref_url.find('/user/') != -1) : 
                            continue
                        if '/shorts/' in ref_url:
                            continue
                                        
                        try:
                            date_line = video_element.find_element(By.CSS_SELECTOR,'#metadata #metadata-line span:nth-child(4)').text

                            content_date = self.to_date(date_line)

                        except:
                            continue

                        if content_date < self.start_date: # 검색 기간보다 전의 데이터 나오면 종료 
                            is_finished = True
                            self.log.debug ('content_date "' + str(content_date) + '" < start_date "' + str(self.start_date) + '"')
                            break
                        elif content_date > self.end_date: # 검색 기간보다 최근의 데이터 나오면 계속 확인  
                            self.log.debug ('content_date "' + str(content_date) + '" > end_date "' + str(self.end_date) + '"')
                            continue 
                        if self.job_type == "M":
                            if keyword in title:
                                v = ref_url.split('&')[0]
                                dic = [k for k in youtube_id_dic.keys() if v in k] 
                                if len(dic) == 0 :            
                                    data['date'] = content_date
                                    data['keyword'] = keyword
                                    youtube_id_dic[ref_url] = data
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

                                v = ref_url.split('&')[0]
                                dic = [k for k in youtube_id_dic.keys() if v in k] 
                                if len(dic) == 0 :            
                                    data['date'] = content_date
                                    data['keyword'] = must_in_kr
                                    youtube_id_dic[ref_url] = data

                    except Exception as e:
                        self.log.error('error: ' + str(e))
                        self.log.error (traceback.print_exc())
                        self.quit_self('db error')
                        continue

        self.log.debug ('youtube_id_dic : ' + str(len(youtube_id_dic)))
        for url,data in youtube_id_dic.items():
            # 아래와 같이 item을 함수의 return으로 받아야만 정상동작한다. (함수 안에서 yeid하면 함수가 실행을 안함)
                item = self.parse_article(url,data)
                yield item


    def parse_article(self,url,data):

        self.driver.get(url)
        self.driver.implicitly_wait(5)
        self.random_sleep() # 이게 없으면 로딩이 덜 되서 크롤링이 안될때가 있음 

        #
        # 기본 정보 (제목, 작성일, 조회수, 좋아요, 싫어요, 채널이름, 조회수) 추출
        #
        item = YoutubeCrawlerItem()
        item['job_id'] = self.job_id
        item['url'] = url.split('&pp')[0]
        item['media'] = '유튜브'
        item['keyword'] = data['keyword']

        try: 
            primary_info = self.driver.find_element(By.CSS_SELECTOR, '#info #info-contents').get_attribute('innerHTML')
            super_title = primary_info.split('force-default-style="" class="style-scope ytd-video-primary-info-renderer">')[1].split('</yt-formatted-string>')[0]
            if super_title.find('<span dir=') != -1: # 샵 태그가 붙은 경우 
                super_title = super_title.split('<span dir="auto" class="style-scope yt-formatted-string">')[1].split('</')[0]
            item['title'] = super_title
        except Exception as e:
            self.log.error ('get super_title: ' + str(e) + ', ' + url)
            return


        try:
            view = primary_info.split('조회수 ')[1].split('회')[0].replace(',','')
            if '없음' in view:
                item['views'] = '0'
            else:
                item['views'] = view
        except:
            item['views'] = '0'
        
        item['date'] = data['date'].strftime('%Y-%m-%dT%H:%M:%S+09:00')


        try:
            like = self.driver.find_element(By.CSS_SELECTOR,'#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button > div.yt-spec-button-shape-next__button-text-content > span').text
            item['like'] = self.to_num(like)

        except:
            item['like'] = 0

        writer_info = self.driver.find_element(By.CSS_SELECTOR, '#upload-info #text a')
        item['writer'] = writer_info.get_attribute('innerHTML').strip()
        item['post_id'] = writer_info.get_attribute('href').split('.com/')[1]

        #
        # 리뷰 추출
        #

        # scroll을 해야 리뷰로 갈 수 있다. 
        self.driver.execute_script("window.scrollTo(0, window.scrollY + 600)")

        self.random_sleep()

        # 리뷰 페이지를 끝까지 로딩
        self.scroll_to_bottom(self.driver)
        self.random_sleep()

        #headless일 때 스크롤 전에는 아래의 XPATH가 잡히질 않음 (headless가 아닌 경우는 잘됨)
        try:
            comment_info = self.driver.find_element(By.XPATH, '//*[@id="count"]/yt-formatted-string').get_attribute('innerHTML')
            item['comment_count'] = comment_info.split('댓글 </span><span dir="auto" class="style-scope yt-formatted-string">')[1].split('</span><span')[0]
        except:
            item['comment_count'] = '0'


        # 리뷰 
        comment_elements = []
        try:                                                
            comment_elements = self.driver.find_elements(By.CSS_SELECTOR, ' #body #main')
        except Exception as e:
            self.log.error('error: ' + str(e))
            self.log.error (traceback.print_exc())
            self.quit_self('db error')

        
        comment_list = []
        for comment_element in comment_elements:
            comment = {} 
            try:
                header = comment_element.find_element(By.CSS_SELECTOR,'#header')
                user_name = header.find_element(By.CSS_SELECTOR,'#header-author a').text
                day_string = header.find_element(By.CSS_SELECTOR,'.published-time-text a').text

                now = datetime.now()
                comment_day = ''
                if day_string.find('일 전') != -1:
                    comment_day = (now - timedelta(days=int(re.search(r'\d+',day_string).group()))).strftime("%Y-%m-%dT%H:%M:%S+09:00")
                elif day_string.find('주 전') != -1:
                    comment_day = (now - timedelta(days=int(re.search(r'\d+',day_string).group()))*7).strftime("%Y-%m-%dT%H:%M:%S+09:00")
                elif day_string.find('개월 전') != -1:
                    comment_day = (now - timedelta(days=int(re.search(r'\d+',day_string).group()))*31).strftime("%Y-%m-%dT%H:%M:%S+09:00")
                elif day_string.find('년 전') != -1:
                    comment_day = (now - timedelta(days=int(re.search(r'\d+',day_string).group()))*365).strftime("%Y-%m-%dT%H:%M:%S+09:00")
                else: # 시간 전 또는 분전 
                    comment_day = now.strftime("%Y-%m-%dT%H:%M:%S+09:00")


                comment_body_page = comment_element.find_element(By.CSS_SELECTOR,'#comment-content #content #content-text')

                comment_text = comment_body_page.text.split('\n')
                like = comment_element.find_element(By.CSS_SELECTOR,'#vote-count-left').text
                if like =='':
                    like = '0'
                comment['date'] = comment_day
                comment['id'] = user_name
                comment['text'] = comment_text
                comment['like'] = self.to_num(like)
                comment_list.append(comment)
            except Exception as e:
                self.log.debug ('comment_list.append except: ' + str(e))
                continue
        item['comment']=comment_list
        
        return item
        

    def go_bottom(self, driver): # 한번에 스크롤 끝까지 내려감
        old_position = 0
        new_position = None
        i = 1
        while new_position != old_position:
            try:
                # Get old scroll position
                old_position = driver.execute_script(
                        ("return (window.pageYOffset !== undefined) ?"
                        " window.pageYOffset : (document.documentElement ||"
                        " document.body.parentNode || document.body);"))

                # Scroll and Sleep 
                driver.execute_script((
                        "var scrollingElement = (document.scrollingElement ||"
                        " document.body);scrollingElement.scrollTop ="
                        " scrollingElement.scrollHeight;"))
                self.random_sleep()

                # Get new position
                new_position = driver.execute_script(
                        ("return (window.pageYOffset !== undefined) ?"
                        " window.pageYOffset : (document.documentElement ||"
                        " document.body.parentNode || document.body);"))

            except: 
                break

            time.sleep (uniform(0.5, 3.0))#contents > ytd-item-section-renderer
            try:
                test = driver.find_element(By.CSS_SELECTOR, f'ytd-item-section-renderer:nth-child({i}) ytd-video-renderer:nth-last-child(1)')
                href = test.find_element(By.CSS_SELECTOR,'#video-title').get_attribute('href')
            except:
                continue
            try:
                content_date = test.find_element(By.CSS_SELECTOR,'#metadata-line > span:nth-child(4)').text
                date = self.to_date(content_date)
                i+=1
                if '/shorts/' in href:
                    continue
                if date < self.start_date:
                    break 
            except:
                break
            


    def scroll_to_bottom(self, driver): # 화면을 600픽셀씩 내려서 끝까지 내려감
        old_position = 0
        new_position = None

        while new_position != old_position:
            try: 
                # Get old scroll position
                old_position = driver.execute_script(
                        ("return (window.pageYOffset !== undefined) ?"
                        " window.pageYOffset : (document.documentElement ||"
                        " document.body.parentNode || document.body);"))

                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, window.scrollY + 600);")
                time.sleep (uniform(0.5, 2.0))

                # Get new position
                new_position = driver.execute_script(
                        ("return (window.pageYOffset !== undefined) ?"
                        " window.pageYOffset : (document.documentElement ||"
                        " document.body.parentNode || document.body);"))
            except: 
                break


    def text_escape(self, text, clear_return = True):
        result_text = ''
        text = html.unescape(text)

        if clear_return:
            for s in text.strip():
                regex = re.compile(r'[\r\n\t\xa0]')
                s = regex.sub('', s)
                result_text = result_text + s
        else:
            for s in text.strip():
                regex = re.compile(r'[\r\t\xa0]')
                s = regex.sub('', s)
		    	# 줄바꿈을 그냥 없애면 윗줄 마지막 단어와 아랫줄 첫 단어가 붙어서 형태소 분석이 제대로 안된다.
                regex = re.compile(r'[\n]') 
                s = regex.sub(' ', s)
                result_text = result_text + s

        return result_text


    def error_page(self, failure):
        request = failure.request
        print('==> url :', request.url)
        url_index = self.start_urls.index(request.url)
        self.board_error[url_index] = True
        
        if failure.check(HttpError):
            response = failure.value.response
            print('HttpError :', response.status, ':', response.url)
            self.update_link(self.crawler_id, self.board_id + "_" + self.board_name[url_index], str(response.status), self.start_urls[url_index], 0)
        elif failure.check(DNSLookupError):
            print('DNSLookupError ::', request.url)
            self.update_link(self.crawler_id, self.board_id + "_" + self.board_name[url_index], 'DNSLookupError', self.start_urls[url_index], 0)
        elif failure.check(TimeoutError, TCPTimedOutError):
            print('TimeoutError ::', request.url)
            self.update_link(self.crawler_id, self.board_id + "_" + self.board_name[url_index], 'TimeoutError', self.start_urls[url_index], 0)


    def random_sleep(self):
        time.sleep (self.secretsGenerator.randrange(1, 3))
    
    
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
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service,options=chrome_options)
        self.driver = driver
    
    def to_num(self,like):
        if '만' in like:
            like = float(like.replace('만',''))
            re = like * 10000
        elif '천' in like:
            like = float(like.replace('천',''))
            re = like * 1000
        else:
            re = like
        return int(re)
    
    
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
        query_str = "SELECT topic, youtube_keyword, must_in_kr,must_co_kr,must_out_kr  FROM crawler_search_keyword ORDER BY num"
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
        
    def to_date(self, date):
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')
        if '스트리밍' in date:
            date = date.split(': ')[1]
        if '분' in date:
            min = int(date.split('분')[0])
            time = datetime.now() - relativedelta(minutes=(min + 1))
        elif '초' in date:
            sec = int(date.split('초')[0])
            time = datetime.now() - relativedelta(seconds=(sec + 1))
        elif '시간' in date:
            hour = int(date.split('시간')[0])
            time = datetime.now() - relativedelta(hours=(hour + 1))
        elif '일' in date:
            day = int (date.split('일')[0])
            time = datetime.now() - relativedelta(days=(day))
        elif '주' in date:
            week = int (date.split('주')[0])
            time = datetime.now() - relativedelta(weeks=(week))
        elif '개월' in date:
            month = int(date.split('개월')[0])
            time = datetime.now() - relativedelta(months=(month))
        else:
            year = int (date.split('년')[0])
            time = datetime.now() - relativedelta(years=(year))
        str_date = time.strftime('%Y-%m-%dT%H:%M:%S+09:00')

        return datetime.strptime(str_date,'%Y-%m-%dT%H:%M:%S+09:00')

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

        self.driver.close()
        self.driver.quit()
        
    def quit_self(self, reason):
        self.log.debug ('quit_self: ' + str(reason))

        self.driver.close()
        self.driver.quit()
        sys.exit()
        

