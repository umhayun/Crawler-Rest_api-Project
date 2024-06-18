from app.model import main_detail_model
from utils.els_utils import ELSUtils


class MainDetailService:

    def __init__(self, job_id):
        self.es = ELSUtils().getConn()
        if job_id is None:
            self.match = {"match_all": {}}
        else:
            self.match = {"match": {
                "job_id": job_id
            }}

    def get_summary(self, num):
        data = main_detail_model.select_summary(self.es, self.match)
        result = ""
        if data == None :
            return {
                "summary": ""
            }
        
        for summary in data['_source']['summary']:
            if summary['community_num'] == num:
                result = summary['summary']
                break
        return {'summary': result}

    def get_community(self, num):
        data = main_detail_model.select_community(self.es, self.match)
        if data == None :
            return {
                "summary": [],
                "communities": []
            }
        
        summary_list = data["_source"]["summary"]
        summary = []
        for list in summary_list:
            if str(list['parent_community_num']) == num:
                sorted_result = sorted(list['summary_detail'], key=lambda x: x['rank'])
                for s in sorted_result:
                    summary.append([s])
        communities_list = data["_source"]["communities"]
        communities = []
        for commu in communities_list:
            if commu['parent_community_num'] == num:
                for c in commu['community_items']:
                    communities.append(c['community_detail'])

        result = {
            "summary": summary,
            "communities": communities
        }
        return result

    def get_media_count(self, num):
        data = main_detail_model.select_media_count(self.es, self.match)
        if data == None :
            return {
                "네이버": [0,0,0,0,0],
                "티스토리": [0,0,0,0,0],
                "유튜브": [0,0,0,0,0],
                "뽐뿌": [0,0,0,0,0],
                "디시인사이드": [0,0,0,0,0]
            }
        
        order = ""

        for c in data['_source']['media_count']:
            if c['parent_community_num'] == num:
                result = c['count_detail']
                order = c['community_order']
        sorted_result = list()

        if order != "" :
            for o in order.split('[')[1].split(']')[0].split(','):
                for r in result:
                    if r['community_num'] == o.strip():
                        sorted_result.append(r)
                        break

        medias = ["네이버_블로그", "네이버_카페", "티스토리", "유튜브", "뽐뿌", "디시인사이드"]
        temp_list = [[], [], [], [], []]

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
            "디시인사이드": temp_list[4]
        }

    def get_issue_process(self, num):
        data = main_detail_model.select_issue_process(self.es, self.match)
        if data == None :
            return {
                'date': [],
                'summary': {}
            }
        
        result = []
        for c in data['_source']['issue_process']:
            if c['parent_community_num'] == num:
                result = c['issue_detail']
        summaries = dict()
        dates = set()

        if len(result) > 0 :
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

    def get_wordcloud(self, num):
        result = []

        data = main_detail_model.select_wordcloud(self.es, self.match)
        if data == None :
            return []

        for c in data['_source']['wordcloud']:
            if c['parent_community_num'] == num:
                result = c['community_wordcloud_data']
        return result

    def get_senti_graph(self, num):
        result = []

        data = main_detail_model.select_senti_graph(self.es, self.match)
        if data == None :
            return []
        
        for c in data['_source']['senti_graph']:
            if c['parent_community_num'] == num:
                result = c['community_senti_data']
        return result
