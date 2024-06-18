import pymysql
import re

from scrapy.utils.project import get_project_settings
from youtubeCrawler.log_util import LogUtil

#INFO :
# 1. 제목에 대해서 stop_word 적용해서 stop_word에 걸리면 아예 처리 안함 
# 2. 제목만 길이가 4미만이면 처리 안함 --> 기존은 댓글도 처리안했으나, 댓글은 처리하게 수정 

class preprocessor:

    def __init__(self, logger):
        self.settings = get_project_settings()
        self.logger = logger

        #DB 연동
        self.conn = pymysql.connect(
            host = self.settings['MARIADB_HOST'],
            port = self.settings['MARIADB_PORT'],
            user = self.settings['MARIADB_USERNM'],
            password = self.settings['MARIADB_PASSWD'],
            db = self.settings['MARIADB_DBNM'], 
            charset = 'utf8')
        self.cur = self.conn.cursor()

        self.stop_word = []
        self.nation_word = []
        self.politic_word = []
        self.delete_word = []
        self.not_comment_word = [] 


    # stopword 데이터 가져오기
    def load_stop_word (self):

        # stop_word = nation and politic word
        self.cur.execute("SELECT word FROM SPECIAL_WORD where type = 'politic' or type = 'nation'")
        res = self.cur.fetchall()      

        for cursor in res:
            self.stop_word.append (cursor[0])

        # nation_word
        self.cur.execute("SELECT word FROM SPECIAL_WORD where type = 'nation'")
        res = self.cur.fetchall()      

        for cursor in res:
            self.nation_word.append (cursor[0])

        # politic_word
        self.cur.execute("SELECT word FROM SPECIAL_WORD where type = 'politic'")
        res = self.cur.fetchall()      

        for cursor in res:
            self.politic_word.append (cursor[0])

        # delete_word
        self.cur.execute("SELECT word FROM SPECIAL_WORD where type = 'delete'")
        res = self.cur.fetchall()      

        for cursor in res:
            self.delete_word.append (cursor[0])

        # not_comment_word
        self.cur.execute("SELECT word FROM SPECIAL_WORD where type = 'not_comment'")
        res = self.cur.fetchall()      

        for cursor in res:
            self.not_comment_word.append (cursor[0])

        self.conn.close()
 

    # stopword 문자가 있는 지 확인
    def check_stop_word (self, text):
        for word in self.stop_word:
            if word in text: 
                self.logger.debug ('stop_word: "' + word + '" is in "' + text + '"')
                return True
        return False    


    # politic 문자가 있는 지 확인
    def check_politic_word (self, text):
        for word in self.politic_word:
            if word in text: 
                self.logger.debug ('politic_word: "' + word + '" is in "' + text + '"')
                return True
        return False    


    # nation 문자가 있는 지 확인
    def check_nation_word (self, text):
        for word in self.nation_word:
            if word in text: 
                self.logger.debug ('nation_word: "' + word + '" is in "' + text + '"')
                return True
        return False    


    # not_comment 문자가 있는 지 확인
    def check_not_comment_word (self, text):
        for word in self.not_comment_word:
            if word in text: 
                self.logger.debug ('not_comment_word: "' + word + '" is in "' + text + '"')
                return True
        return False    


    # delete_word에 있는 문자열을 지우고, 지운 결과로 생긴 공백을 최소화 해서 반환함 
    #   예) 정말 ㅋㅋㅋ 좋아요 -> 정말  좋아요 --> 정말 좋아요
    #   빈문자열이 되면 None을 반환 
    def delete_special_word (self, text):
        for word in self.delete_word:
            text = text.replace(word, '')

        text = re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z\s]", "", string=text)
        #text = re.sub(pattern=r"[=\ㆍ\.\+]", repl=" ", string=text)
        #text = re.sub(pattern=r"[,\"?!#$&=*~]", repl=" ", string=text)
        #text = re.sub(pattern=r"[\'\`\\]", repl=" ", string=text)
        #text = re.sub(pattern=r"[\●\-\★\■\<\>\@\◆\♥\☜\/\_\;\:]", repl="", string=text)
        #text = re.sub(pattern=r"[\[\]\{\}\‘\’\`\…\《\》]", repl=" ", string=text)
        #text = re.sub(pattern=r"[-ㆍ\…\^^\^0^]", repl=" ", string=text)
        #text = re.sub(pattern=r"[\【\】\◇\ⓒ\:\“\”\◀\▶\☎\△\▲\(\)\.]", repl=" ", string=text)

        text.strip()
        temp_sp = text.split()
        if len(temp_sp) != 0:
            return ' '.join(temp_sp)
        
        return None
