from datetime import datetime

import pymysql
from utils.logger import Log
from utils.mysql_pool import MysqlPool


class RelatedWordService:
    def __init__(self):
        self.db_conn = MysqlPool().get_conn()
        self.db_cursor = self.db_conn.cursor(pymysql.cursors.DictCursor)

    def select_types(self):
        sql = 'SELECT distinct category FROM ASSOC_KEYWORD;'
        self.db_cursor.execute(sql)
        result = self.db_cursor.fetchall()
        self.db_conn.close()
        res_list = []
        for c in result:
            res_list.append(c['category'])
        return res_list

    def select_data(self, cate):
        if cate == None:
            sql = 'SELECT * from ASSOC_KEYWORD ORDER by category, keyword'
        else:
            sql = f'SELECT * from ASSOC_KEYWORD where category="{cate}" ORDER by category, keyword'
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
        sql = '''
            INSERT INTO ASSOC_KEYWORD (category, keyword, update_date)
            VALUES (%(category)s, %(keyword)s, %(date)s)
        '''
        data['date'] = datetime.now()
        try:
            res = self.db_cursor.execute(sql, data)
            result['response'] = 'success'
        except Exception as e:
            Log.errer(e)
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

    def select_one_data(self, cate, keyword):
        sql = f"SELECT * from ASSOC_KEYWORD where category='{cate}' and keyword='{keyword}'"
        self.db_cursor.execute(sql)
        result = self.db_cursor.fetchone()
        self.db_conn.close()
        
        for key, value in result.items():
            if 'update_date' in key and value is not None:
                result[key] = value.strftime('%Y-%m-%d %H:%M:%S')

        return result

    def update_data(self, cate, keyword, data):
        result = {}
        sql = '''
            UPDATE ASSOC_KEYWORD SET
                category=%s,
                keyword=%s,
                update_date=%s
            where category=%s and keyword=%s
        '''
        params = [data['category'], data['keyword'], datetime.now(), cate, keyword]
        try:
            res = self.db_cursor.execute(sql, params)
        except Exception as e:
            Log.error(e)
            res = 0
            result['response'] = "fail"
        finally:
            if res != 0:
                self.db_conn.commit()
                result['response'] = "success"
            else:
                result['response'] = "fail"
            self.db_conn.close()

        return result

    def delete_data(self, cate, keyword):
        result = {}
        sql = f'DELETE from ASSOC_KEYWORD where category="{cate}" and keyword="{keyword}"'
        try:
            res = self.db_cursor.execute(sql)
        except Exception as e:
            Log.error(e)
            result['response'] = "fail"
            res = 0
        finally:
            if res != 0:
                self.db_conn.commit()
                result['response'] = "success"
            else:
                result['response'] = "fail"
            self.db_conn.close()

        return result
