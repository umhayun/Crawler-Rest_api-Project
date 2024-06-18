import hashlib
from datetime import datetime

import pymysql
from utils.logger import Log
from utils.mysql_pool import MysqlPool


class UserService:
    def __init__(self):
        self.db_conn = MysqlPool().get_conn()
        self.db_cursor = self.db_conn.cursor(pymysql.cursors.DictCursor)

    def select_data(self):
        sql = 'SELECT * FROM USER ORDER BY id;'
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
        sql = f'select count(*) as re from USER where id = "{data["id"]}"'
        self.db_cursor.execute(sql)
        check = self.db_cursor.fetchone()
        result = {}
        Log.debug("check :: " + check)
        if check['re'] == 0:
            sql = '''INSERT INTO USER (id,password,name,tel,department,email,create_date,update_date)
                    VALUES (%(id)s,%(password)s,%(name)s,%(tel)s,%(department)s,%(email)s,%(create_date)s,%(update_date)s)'''
            data['password'] = hashlib.sha256(data['password'].encode()).hexdigest()
            data['create_date'] = datetime.now()
            data['update_date'] = datetime.now()
            self.db_cursor.execute(sql, data)
            self.db_conn.commit()
            result['response'] = 'success'
        else:
            result['response'] = 'fail'
            result['message'] = 'duplicated'
        self.db_conn.close()
        return result

    def select_one_data(self, id):
        sql = f'select * from USER where id = "{id}"'
        self.db_cursor.execute(sql)
        result = self.db_cursor.fetchone()
        self.db_conn.close()
        for key, value in result.items():
            if 'date' in key and value is not None:
                result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        self.db_conn.close()
        return result

    def update_data(self, id, new):
        result = {}
        sql = 'UPDATE USER SET password=%s,name=%s,tel=%s,department=%s,email=%s,update_date=%s where id=%s'
        new['password'] = hashlib.sha256(new['password'].encode()).hexdigest()
        param = [new['password'], new['name'], new['tel'], new['department'], new['email'], datetime.now(), id]
        res = self.db_cursor.execute(sql, param)
        if res != 0:
            self.db_conn.commit()
            result['response'] = "success"
        else:
            result['response'] = "fail"
        self.db_conn.close()
        return result

    def delete_data(self, id):
        result = {}
        sql = f'DELETE FROM USER WHERE id = "{id}"'
        res = self.db_cursor.execute(sql)
        if res != 0:
            self.db_conn.commit()
            result['response'] = "success"
        else:
            result['response'] = "fail"
        self.db_conn.close()
        return result

    def check_login(self, id, pw):
        result = {}
        try:
            data = self.select_one_data(id)

            new_pw = hashlib.sha256(pw.encode()).hexdigest()
            if data['password'] == new_pw:
                result['response'] = "success"
            else:
                result['response'] = "fail"
        except:
            result['response'] = "fail"
        return result
