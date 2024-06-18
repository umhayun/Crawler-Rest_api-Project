import pymysql
from utils.mysql_pool import MysqlPool


class CrawlerStateService:
    def __init__(self):
        self.db_conn = MysqlPool().get_conn()
        self.db_cursor = self.db_conn.cursor(pymysql.cursors.DictCursor)

    def get_data(self):
        sql = 'SELECT * FROM CRAWLER_STATUS ORDER BY job_id,sub_id;'
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
