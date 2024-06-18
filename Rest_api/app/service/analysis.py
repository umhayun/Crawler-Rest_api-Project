from datetime import datetime

import pymysql
import requests
from app.model import analysis_model
from flask import current_app
from utils.els_utils import ELSUtils
from utils.logger import Log
from utils.mysql_pool import MysqlPool


class AnalysisService:
    def __init__(self):
        self.es = ELSUtils().getConn()

    def get_analysis(self, include, exclude, media, start, end):
        query = ""
        search_keyword = include.split("|")
        search_keyword = [v for v in search_keyword if v]  # 공백 제거
        if len(search_keyword) == 1:
            query = search_keyword[0]
        else:
            query = ') OR ('.join(search_keyword)
        # search_keyword = include.strip().replace('|',') OR (').replace(','," AND ")
        query = query.replace(',', " AND ")
        query = f"({query})"
        exclude_list = exclude.split(',')
        for text in exclude_list:
            if text.strip() == "":
                continue
            query = query + f" NOT ({text})"
        data = analysis_model.select_analysis_count(self.es, query, media, start, end)
        return {"count": data["value"]}

    def get_data(self):
        db_conn = MysqlPool().get_conn()
        db_cursor = db_conn.cursor(pymysql.cursors.DictCursor)

        sql = 'SELECT * FROM RISSUE_RUN_STATUS WHERE user_id!="admin" ORDER BY job_start_date DESC ;'
        db_cursor.execute(sql)
        result = db_cursor.fetchall()

        db_cursor.close()
        db_conn.close()

        res_list = []
        for data in result:
            for key, value in data.items():
                if 'date' in key and value is not None:
                    data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                if 'louvain_resolution' in key:
                    data[key] = str(data[key])
            res_list.append(data)
        return res_list

    def insert_data(self, data):
        db_conn = MysqlPool().get_conn()
        db_cursor = db_conn.cursor(pymysql.cursors.DictCursor)

        result = {}
        data['job_start_date'] = datetime.now()
        sql = '''
        INSERT INTO RISSUE_RUN_STATUS (job_id, user_id, analysis_name,media,louvain_resolution, job_start_date, 
                                     search_start_date,search_end_date, incexc_keyword, count)
        VALUES (%(job_id)s, %(user_id)s, %(analysis_name)s,%(media)s, %(louvain_resolution)s, %(job_start_date)s,
        %(search_start_date)s, %(search_end_date)s,%(incexc_keyword)s,%(count)s)
      '''
        try:
            res = db_cursor.execute(sql, data)
            result['response'] = 'success'
            if res > 0:
                db_conn.commit()
                result['response'] = f'/analysis/start/{data["job_id"]}'
            else:
                db_conn.rollback()
                result['response'] = "fail(res=0)"
        except Exception as e:
            Log.error('error: ' + str(e))
            db_conn.rollback()
            result['response'] = 'fail(insert)'
        finally:
            db_cursor.close()
            db_conn.close()
            
        return result

    def analysis_start(self, job_id):
        url = f"http://{current_app.config['ANALYSIS_SERVICE_HOST']}:{current_app.config['ANALYSIS_SERVICE_PORT']}/rest/1.0/rissue/runcustom/{job_id}"
        response = requests.get(url=url)
        result = eval(response.text)
        return result

    def delete_analysis_data(self, job_id):
        db_conn = MysqlPool().get_conn()
        db_cursor = db_conn.cursor(pymysql.cursors.DictCursor)

        sql = '''
            DELETE FROM RISSUE_RUN_STATUS WHERE job_id = %s
        '''
        res = db_cursor.execute(sql, (job_id,))

        if res > 0:
            db_conn.commit()
        else:
            db_conn.rollback()

        db_cursor.close()
        db_conn.close()

        return res
