import pymysql
from dbutils.pooled_db import PooledDB
from flask import current_app


class MysqlPool(object):
    __pool = None;

    def __init__(self):
        if not MysqlPool.__pool:

            self.__make_pool()


    def __make_pool(self):
        MysqlPool.__pool = PooledDB(
            creator=pymysql,
            mincached=10, 
            maxcached=20,
            maxshared=10, 
            maxconnections=25, 
            blocking=True,
            maxusage=0, 
            setsession=None, 
            reset=True,

            host=current_app.config['MARIADB_HOST'], 
            port=current_app.config['MARIADB_PORT'],
            user=current_app.config['MARIADB_USER'], 
            password=current_app.config['MARIADB_PW'],
            db=current_app.config['MARIADB_DBNM'],
            # charset=current_app.config['MYSQL_CHARSET'],
        )
    

    def get_conn(self):
        self._conn = MysqlPool.__pool.connection();

        return self._conn
