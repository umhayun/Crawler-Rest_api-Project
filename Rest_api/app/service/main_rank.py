import json
from datetime import datetime

from app.model import main_rank_model
from dateutil.relativedelta import relativedelta
from utils.els_utils import ELSUtils


class MainRankService:
    def __init__(self):
        self.es = ELSUtils().getConn()

    def get_weekly(self):
        data = main_rank_model.select_weekly_rank(self.es)
        result = data['_source']['summary']
        return result

    def get_daily(self):
        recent = main_rank_model.select_weekly_rank(self.es)
        recent_date = recent['_source']['job_start_dt'].split(".")[0]
        search_date = []

        for i in range(1, 6):
            # 가장 최근 데이터 - 1day부터 5일
            date = (datetime.strptime(recent_date, "%Y-%m-%dT%H:%M:%S")-relativedelta(days=i)).strftime('%Y-%m-%dT%H')
            search_date.append(date)
        res = main_rank_model.select_daily_rank(self.es, search_date)
        result = res['hits']['hits']
        result.reverse()
        return result

    def get_detail(self, num):
        res = main_rank_model.select_detail(self.es, num)
        result = res['_source']

        summary = result['summary']
        summary_list = list()
        for item in summary:
            if item['parent_community_num'] == num:
                summary_list = item['summary_detail']
                break
        graph = ''
        for item in result['graph'][0]:
            if str(item['parent_community_num']) == num:
                graph = item['graph']
                break

        graph_json = json.loads(graph.replace("'", '"').replace("False", "false"))
        nodes = graph_json['nodes']
        links = graph_json['links']['links']
        return {'summary': summary_list, 'graph': {'nodes': nodes, 'links': links}}
