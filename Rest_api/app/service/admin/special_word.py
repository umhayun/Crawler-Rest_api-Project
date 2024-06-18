from datetime import datetime

import pymysql
from app.model.admin.special_word_model import delete_specialword
from utils.els_utils import ELSUtils
from utils.logger import Log
from utils.mysql_pool import MysqlPool


class SpecialWordService:
    def __init__(self):
        self.db_conn = MysqlPool().get_conn()
        self.db_cursor = self.db_conn.cursor(pymysql.cursors.DictCursor)
        self.es = ELSUtils().getConn()

    def select_data(self, type):
        if type == None:
            sql = 'SELECT * FROM SPECIAL_WORD ORDER BY type, word;'
        else:
            sql = f'SELECT * FROM SPECIAL_WORD WHERE type ="{type}" ORDER BY type, word;'
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

    def select_one(self, word):
        sql = f'SELECT * FROM SPECIAL_WORD WHERE word ="{word}";'
        self.db_cursor.execute(sql)
        result = self.db_cursor.fetchone()
        self.db_conn.close()

        for key, value in result.items():
            if 'date' in key and value is not None:
                result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        return result

    def update_data(self, old, new):
        result = {}
        sql = f"UPDATE SPECIAL_WORD SET type = '{new['type']}', word = '{new['word']}' , update_date = '{datetime.now()}' WHERE word='{old}'"
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

    def insert_data(self, data):
        result = {}
        data['word'] = data['word'].strip()
        sql = f'SELECT * FROM SPECIAL_WORD WHERE type ="{data["type"]}" and word = "{data["word"]}" ;'
        self.db_cursor.execute(sql)
        check = self.db_cursor.fetchone()
        if check == None:
            sql = "INSERT INTO SPECIAL_WORD (type,word) VALUES (%(type)s,%(word)s)"
            self.db_cursor.execute(sql, data)
            if data['remove'] == 'Y' and data['type'] != 'delete':
                delete_specialword(self.es,data)
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

    def delete_data(self, word):
        result = {}
        sql = f'DELETE FROM SPECIAL_WORD WHERE word ="{word}"'
        res = self.db_cursor.execute(sql)
        if res != 0:
            self.db_conn.commit()
            result['response'] = "success"
        else:
            result['response'] = "fail"
        return result
