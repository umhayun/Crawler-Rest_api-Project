import pymysql
from app.model import analysis_detail_model
from utils.els_utils import ELSUtils
from utils.mysql_pool import MysqlPool


class AnalysisDetailService:
    def __init__(self):

        self.db_conn = MysqlPool().get_conn()
        self.db_cursor = self.db_conn.cursor(pymysql.cursors.DictCursor)
        self.es = ELSUtils().getConn()

    def get_summary(self, id):
        sql = f"SELECT analysis_name FROM RISSUE_RUN_STATUS where job_id='{id}'"
        self.db_cursor.execute(sql)
        result = self.db_cursor.fetchone()
        self.db_conn.close()
        return {'summary': result['analysis_name']}

    def get_community(self, id):
        data = analysis_detail_model.select_community(self.es, id)
        if data == None :
            return {
                "summary": [],
                "communities": []
            }
        community_list = data["_source"]["communities"]
        summary = []
        communities = []
        for com in community_list:
            summ = {}
            summ['rank'] = com['rank']
            summ['community_num'] = com['community_num']
            summ['summary'] = com['summary']
            summ['count'] = len(com['community_detail'])
            summary.insert(summ['rank'], [summ])
            communities.append(com['community_detail'])
        result = {
            "summary": summary,
            "communities": communities
        }
        return result

    def get_media_count(self, id):
        data = analysis_detail_model.select_media_count(self.es, id)
        if data == None :
            return {
                "네이버": [0,0,0,0,0],
                "티스토리": [0,0,0,0,0],
                "유튜브": [0,0,0,0,0],
                "뽐뿌": [0,0,0,0,0],
                "디시인사이드": [0,0,0,0,0]
            }
        
        media_count_list = data['_source']['media_count']
        sorted_result = sorted(media_count_list, key=lambda x: x['rank'])

        medias = ["네이버_블로그", "네이버_카페", "티스토리", "유튜브", "뽐뿌",  "에프엠코리아", "디시인사이드"]
        temp_list = [[], [], [], [], [], []]
        for item in sorted_result:
            count = item['num_count_per_media']
            for idx, value in enumerate(medias):
                temp = 0
                if value in count:
                    temp += count[value]
                if idx == 0:
                    temp_list[idx].append(temp)
                elif idx == 1:
                    prev = temp_list[0].pop()
                    temp_list[0].append(prev + temp)
                else:
                    temp_list[idx-1].append(temp)
        return {
            "네이버": temp_list[0],
            "티스토리": temp_list[1],
            "유튜브": temp_list[2],
            "뽐뿌": temp_list[3],
            "디시인사이드": temp_list[5]
        }

    def get_issue_process(self, id):
        data = analysis_detail_model.select_issue_process(self.es, id)
        if data == None :
            return {
                'date': [],
                'summary': {}
            }
        
        result = data['_source']['issue_process']
        summaries = dict()
        dates = set()
        for issue in result:
            dates.add(issue['date'])
            l = len(summaries)
            summary = issue['summary']
            if l == 0:
                summaries[summary] = [issue['count']]
            elif l > 0 and summary not in summaries.keys():
                summaries[summary] = [issue['count']]
            elif l > 0 and summary in summaries.keys():
                summaries[summary].append(issue['count'])
        date_list = list(dates)
        date_list.sort()

        return {
            'date': date_list,
            'summary': summaries
        }

    def get_wordcloud(self, id):
        data = analysis_detail_model.select_wordcloud(self.es, id)
        if data == None :
            return []
        
        result = data['_source']['wordcloud']

        return result

    def get_senti_graph(self, id):
        data = analysis_detail_model.select_senti_graph(self.es, id)
        if data == None :
            return []
        
        result = data['_source']['senti_graph']
        return result
