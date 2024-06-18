import sys
import scrapy
from datetime import datetime, timedelta
from blogCrawler.items import BlogCrawlerItem
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
from fake_useragent import UserAgent
from blogCrawler.log_util import LogUtil


class BlogSpider(scrapy.Spider):
    name = 'blogSpider'

    search_blog = "https://section.blog.naver.com/Search/Post.naver?rangeType=PERIOD&orderBy=sim&startDate={}&endDate={}&keyword=keystring&pageNo=1"

    headers = {'sec-fetch-mode': 'cors', 'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
               'accept': '*/*', 'sec-fetch-site': 'same-origin'}
    
    def __init__(self, job_id='', sub_id='', *args, **kwargs):
        super(BlogSpider, self).__init__(*args, **kwargs) 

        self.settings = get_project_settings()
        self.selenium_flag = True
        # 실행 정보 확인 
        # job_id는 한번에 실행되는 job의 단위, sub_id는 실행되는 crawler별로 생성
        self.job_id = job_id
        self.sub_id = sub_id 

        log_util = LogUtil('naverBlogCrawler' + '-' + str(sub_id))
        self.log = log_util.get_logger()  # Scrapy에 logger가 정의되어 있어서 self.logger 사용 못함 
        
        self.init_driver()
        self.init_mysql()

        # 검색 keyword 출력
        self.filtering_keywords = self.get_keyword()    

        # 기타 검색 조건 출력
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
        yield scrapy.Request(url=self.search_blog, callback=self.get_search_result)                     

    
    def get_search_result (self, response): 
        self.start_page = math.ceil(self.start_index / 7)
        self.end_page = math.ceil(self.end_index / 7) 
        self.log.debug ('start_date: ' + str(self.start_date))
        self.log.debug ('end_date: ' + str(self.end_date))
        self.log.debug ('start_page: ' + str(self.start_page))
        self.log.debug ('end_page: ' + str(self.end_page))

        while self.start_date.strftime('%Y-%m-%d') <= self.end_date.strftime('%Y-%m-%d'):
            blog_list_url = self.search_blog.format(self.end_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d'))
            blog_id_dic = self.get_blog_list(blog_list_url)
            self.end_date -= relativedelta(days=1)
            self.driver.delete_all_cookies()
            for key, value in blog_id_dic.items(): 
                yield self.parse_blog(key, value)


    # keyword 들의 특정 날짜에 대한 blog id list를 구한 후, 해당 blod_id를 크롤링 
    def get_blog_list (self, ori_blog_list_url):
        
        # 키워드별로 실행
        blog_id_dic = dict()
        manual_num = 0
        for filtering_keyword in self.filtering_keywords :         
            if self.job_type == "M":
                manual_num += 1
                if manual_num > 1:
                    break     
                filtering_keyword['search_keyword'] = self.keywords
                self.log.debug ('topic: ' + str(filtering_keyword['search_keyword']))
            else:
                self.log.debug ('topic: ' + filtering_keyword['topic'])
            for keyword in filtering_keyword['search_keyword'] :           
                if '&' in keyword:
                    keyword = keyword.replace('&',"%26") 
                blog_list_url = ori_blog_list_url.replace('keystring', keyword)
                blog_list_url = blog_list_url.split('&pageNo=')[0] + '&pageNo=' + str(self.start_page)
                self.log.debug ('blog_list_url: ' + blog_list_url)

                self.driver.get(blog_list_url)
                self.random_sleep()

                # 크롤링 시작 페이지와 끝 페이지 계산
                try:
                    content_count = self.driver.find_element(By.CSS_SELECTOR,'.search_number').text.split('건')[0]
                    last_page = math.ceil(float(content_count.replace(',', '')) / 7)
                    self.log.debug ('content_count: ' + str(content_count))
                    self.log.debug ('last_page: ' + str(last_page))
                    
                    if self.start_page > last_page: 
                        continue
                    if self.start_page > 572: 
                        continue
                    end_page = min (last_page, self.end_page, 572)
                    self.log.debug ('end_page = ' + str(end_page))
                except Exception as e:
                    self.selenium_flag = False
                    self.log.error ('get page error: ' + blog_list_url)
                    self.log.error (traceback.print_exc())
                    continue

                # 지정된 페이지들에 대한 크롤링 시작 
                for i in range(self.start_page, end_page + 1):
                    try:
                        list_page = self.driver.find_element(By.XPATH, '/html/body/ui-view/div/main/div/div/section/div[2]')
                        blog_elements = list_page.find_elements(By.CSS_SELECTOR,".list_search_post .desc_inner")
                        # if len(blog_elements) >= 1:  
                        #     blog_elements.pop(0) # 첫번째꺼는 블로그가 아님                       
                        for blog_element in blog_elements: 
                            title_element = blog_element.find_element(By.CSS_SELECTOR,".title").text
                            url = blog_element.get_attribute('href')
                            if self.job_type == "M":
                                if keyword in title_element :                                                                     
                                    self.log.debug ('title: ' +title_element)
                                    value = blog_id_dic.get(url)
                                    if value == None:
                                        blog_id_dic[url] = keyword
                                    else:
                                        self.log.debug ('blog_id_dic[url] exist: ' + url)      
                            else :
                                for must_in_kr in filtering_keyword['must_in_kr']:
                                    # 필수키워드
                                    if must_in_kr not in title_element:
                                        # self.log.debug (f'{must_in_kr}must_in keyword is not in "' + title_element + '"')
                                        continue                     
                                    # 제외키워드                      
                                    match_out_kr = re.match(filtering_keyword['must_out_kr'], title_element)
                                    if match_out_kr is not None:
                                        # self.log.debug ('out keyword is not in "' + title_element + '"')
                                        continue
                                    # 포함키워드
                                    match_co_kr = re.match(filtering_keyword['must_co_kr'], title_element)
                                    
                                    if match_co_kr is None:
                                        # self.log.debug ('co keyword is not in "' + title_element + '"')
                                        continue
                                    self.log.debug ('title: ' +title_element)
                                    value = blog_id_dic.get(url)
                                    if value == None:
                                        blog_id_dic[url] = must_in_kr
                                    else:
                                        self.log.debug ('blog_id_dic[url] exist: ' + url)                                        
                                
                        self.log.debug ('blog_id_dic count: ' +str(len(blog_id_dic)))

                        blog_list_url = blog_list_url.split('&pageNo=')[0] + '&pageNo=' + str(i+1)
                        self.driver.get(blog_list_url)
                        self.log.debug ('blog_list_url: ' + blog_list_url)
                        
                        self.random_sleep()

                    except Exception as e:
                        self.log.error ('get list error: ' + blog_list_url)
                        self.log.error ('error: ' + str(e))
                        self.log.error (traceback.print_exc())

                        blog_list_url = blog_list_url.split('&pageNo=')[0] + '&pageNo=' + str(i+1)
                        self.driver.get(blog_list_url)
                        self.log.debug ('blog_list_url: ' + blog_list_url)
                        self.random_sleep()
        self.driver.delete_all_cookies()
        self.log.debug ('total blog_id_dic count: ' +str(len(blog_id_dic)))
        return blog_id_dic

    
    def parse_blog(self, url, keywords):
        iframe_url = 'https://blog.naver.com/PostView.naver?blogId={}&logNo={}&redirect=Dlog&widgetTypeCall=true&directAccess=false'                  
        iframe_url = iframe_url.format(url.split('/')[3], url.split('/')[4])
        self.log.debug ('blog url: ' + iframe_url)

        self.driver.get(iframe_url)
        self.random_sleep()

        item = BlogCrawlerItem()
        try:
            item['job_id'] = self.job_id
            item['media'] = '네이버_블로그'
            item['keywords'] = keywords
            item['url'] = url
            item['date'] = self.to_date(self.driver.find_element(By.CSS_SELECTOR,'.se_publishDate').text)

            try: 
                item['title']= self.driver.find_element(By.CSS_SELECTOR,'.se-title-text span').text
            except Exception as e:
                self.log.debug ('error: ' + str(e))
                self.log.error (traceback.print_exc())
                item['title']= self.driver.find_element(By.CSS_SELECTOR,'.se_textarea').text
                self.log.debug (item['title'])

            contents= self.driver.find_elements(By.CSS_SELECTOR, '.se-section-text span')
            item['content']= self.content_list(contents)
            item['writer'] = self.driver.find_element(By.CSS_SELECTOR, '.writer ').text.strip()

            a = self.driver.find_element(By.CSS_SELECTOR, '.post-btn > .wrap_postcomment')
            try:
                item['like'] = a.find_element(By.CSS_SELECTOR, ' .area_sympathy em._count').get_attribute('innerHTML')
                if item['like'] == '':
                    item['like'] = '0'
            except:
                item['like'] = '0'

            try:
                comment_cnt = a.find_element(By.CSS_SELECTOR, ' .area_comment ._commentCount').text
                if comment_cnt != '':
                    item['comment'] = self.parse_comment()
                else:
                    item['comment'] = []
            except:
                item['comment'] = []

        except Exception as e:
            self.log.error ('error: ' + str(e))
            self.log.error (traceback.print_exc())

        return item

 
    def parse_comment(self):
        comment_list=[]
        try:
            act = ActionChains(self.driver)
            btn = self.driver.find_element(By.CSS_SELECTOR, 'div.post-btn div.area_comment a')
            act.click(btn).perform()
            self.random_short_sleep()

            comments = self.driver.find_elements(By.CSS_SELECTOR, '.u_cbox_comment')
            for i in comments:
                comment = {}          
                if i.find_element(By.CSS_SELECTOR,' .u_cbox_contents').text!='':
                    str = i.get_attribute('data-info')
                    commentNo = str.lstrip("commentNo:'")
                    parent_no = str.split("parentCommentNo:")[1]
                    comment['id'] = str(commentNo.split("'")[0])
                    comment['parentId'] = parent_no.split("',")[0].strip("'")
                    comment['nickname'] = i.find_element(By.CSS_SELECTOR,'.u_cbox_nick').text
                    comment['text'] = i.find_element(By.CSS_SELECTOR,' .u_cbox_contents').text.replace('\n',' ')
                    comment['date'] = self.to_date(i.find_element(By.CSS_SELECTOR,' .u_cbox_date').text)
                    comment_list.append(comment)
        except:
            pass
        return comment_list
    

    def content_list(self,contents):
        content = []
        for c in contents:
            if c.text.strip()=='' or c.text.strip()=='\u200b':
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
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-crash-reporter")
        chrome_options.add_argument("--disable-oopr-debug-crash-dump")
        chrome_options.add_argument("--no-crash-upload")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-low-res-tiling")
        chrome_options.add_argument("--noconsole")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches',['enable-logging'])
        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(options=chrome_options,service=service)
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
            time = datetime.strptime(date, '%Y. %m. %d. %H:%M')
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
        time.sleep(self.secretsGenerator.uniform(0.7, 1.3))


    def random_short_sleep(self):
        time.sleep(self.secretsGenerator.uniform(0.3, 0.5))


    def get_text_by_selector(self, selector):
        return self.driver.find_element(By.CSS_SELECTOR, selector).text

    def get_keyword(self):
        query_str = "SELECT topic,blog_keyword,must_in_kr,must_co_kr,must_out_kr  FROM crawler_search_keyword ORDER BY num"
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
        query_str = f"UPDATE CRAWLER_STATUS SET status = 'C', crawler_end_date = '" + cur_date.strftime('%Y-%m-%d %H:%M:%S') + \
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



