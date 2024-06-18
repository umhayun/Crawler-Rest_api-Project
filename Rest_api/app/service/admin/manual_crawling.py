from datetime import datetime

import pymysql
from utils.logger import Log
from utils.mysql_pool import MysqlPool


class ManualCrawlingService:
    def __init__(self):
        self.db_conn = MysqlPool().get_conn()
        self.db_cursor = self.db_conn.cursor(pymysql.cursors.DictCursor)

    def get_data(self):
        sql = "SELECT * from CRAWLER_STATUS where type ='M' ORDER by job_id desc"
        self.db_cursor.execute(sql)
        result = self.db_cursor.fetchall()
        self.db_conn.close()
        res_list = []
        for data in result:
            for key, value in data.items():
                if 'date' in key and value is not None:
                    data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            res_list.append(data)

        return res_list

    def insert_data(self, data):
        media_list = dict()
        media_list['naver_blog'] = {
            'search_start_index': 1,
            'search_end_index': 4000
        }
        media_list['naver_cafe'] = {
            'search_start_index': 1,
            'search_end_index': 1200
        }
        media_list['dc'] = {
            'search_start_index': 0,
            'search_end_index': 0
        }
        media_list['ppomppu'] = {
            'search_start_index': 0,
            'search_end_index': 0
        }
        media_list['fm'] = {
            'search_start_index': 1,
            'search_end_index': 10000
        }
        media_list['youtube'] = {
            'search_start_index': 0,
            'search_end_index': 0
        }
        media_list['tstory'] = {
            'search_start_index': 1,
            'search_end_index': 1000
        }
        crawler_name = data['crawler_name']
        search_start_date = datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S')
        search_end_date = datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M:%S')
        period = search_end_date - search_start_date

        data['job_id'] = f"M-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        data['sub_id'] = 'sub1'
        data['job_date'] = datetime.now()
        data['search_start_date'] = search_start_date
        data['search_end_date'] = search_end_date
        data['period'] = period.days + 1
        data['search_start_index'] = media_list[crawler_name]['search_start_index']
        data['search_end_index'] = media_list[crawler_name]['search_end_index']

        result = {}

        sql = '''
            INSERT INTO CRAWLER_STATUS(job_id, sub_id, job_date, crawler_name, keyword, period, search_start_date, search_end_date, search_start_index, search_end_index)
            VALUES (%(job_id)s, %(sub_id)s, %(job_date)s, %(crawler_name)s, %(keyword)s, %(period)s, %(search_start_date)s, %(search_end_date)s, %(search_start_index)s, %(search_end_index)s)
        '''

        try:
            res = self.db_cursor.execute(sql, data)
            result['response'] = 'success'
        except Exception as e:
            Log.error(e)
            result['response'] = 'fail'
            res = 0
        finally:
            if res != 0:
                self.db_conn.commit()
                result['response'] = "success"
            else:
                result['response'] = "fail"
            self.db_conn.close()

        return result
