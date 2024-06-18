from datetime import datetime

import pymysql
from utils.logger import Log
from utils.mysql_pool import MysqlPool


class SentiKeywordService:
    def __init__(self):
        self.db_conn = MysqlPool().get_conn()
        self.db_cursor = self.db_conn.cursor(pymysql.cursors.DictCursor)

    def select_types(self):
        sql = 'SELECT distinct category FROM SENTI_KEYWORD'
        self.db_cursor.execute(sql)
        res = self.db_cursor.fetchall()
        self.db_conn.close()
        res_list = []
        for c in res:
            res_list.append(c['category'])
        return res_list

    def select_data(self, cate):
        if cate == None:
            sql = 'SELECT * FROM SENTI_KEYWORD ORDER BY category, keyword;'
        else:
            sql = f'SELECT * FROM SENTI_KEYWORD WHERE category ="{cate}" ORDER BY category, keyword;'

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
        result = {}
        sql = f'SELECT * FROM SENTI_KEYWORD WHERE category ="{data["category"]}" and keyword = "{data["keyword"]}" ;'
        self.db_cursor.execute(sql)
        check = self.db_cursor.fetchone()
        Log.debug("check :: " + check)
        if check == None:
            sql = "insert SENTI_KEYWORD (category,keyword) VALUES (%(category)s,%(keyword)s)"
            self.db_cursor.execute(sql, data)
            self.db_conn.commit()
            try:
                self.db_conn.commit()
                result['response'] = 'success'
            except Exception as e:
                Log.error(e)
                result['response'] = 'fail'
                result['message'] = 'query error'
        else:
            result['response'] = 'fail'
            result['message'] = 'duplicated'
        return result

    def select_one_data(self, cate, keyword):
        sql = f'SELECT * FROM SENTI_KEYWORD WHERE category ="{cate}" and keyword = "{keyword}" ;'
        self.db_cursor.execute(sql)
        result = self.db_cursor.fetchone()
        self.db_conn.close()

        for key, value in result.items():
            if 'date' in key and value is not None:
                result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        return result

    def update_data(self, cate, keyword, data):
        result = {}
        sql = f"UPDATE SENTI_KEYWORD SET category = '{data['category']}', keyword = '{data['keyword']}' , update_date = '{datetime.now()}'WHERE category='{cate}' and keyword ='{keyword}'"
        try:
            res = self.db_cursor.execute(sql)
            if res != 0:
                self.db_conn.commit()
                result['response'] = 'success'
            else:
                result['response'] = "fail"
        except Exception as e:
            Log.error(e)
            result['response'] = 'fail'
            result['message'] = 'query error'
        return result

    def delete_data(self, cate, keyword):
        result = {}
        sql = f'DELETE FROM SENTI_KEYWORD WHERE category = "{cate}" and keyword ="{keyword}"'
        res = self.db_cursor.execute(sql)
        if res != 0:
            self.db_conn.commit()
            result['response'] = "success"
        else:
            result['response'] = "fail"
        return result
