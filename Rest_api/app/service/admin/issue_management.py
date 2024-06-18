from utils.els_utils import ELSUtils
from app.model.admin import issue_management_model 

class IssueManagementService:
    def __init__(self):
        self.es = ELSUtils().getConn()

    def search_issue_dates(self):
        return issue_management_model.issue_dates(self.es)

    def search_issue_data(self, date):
        result = issue_management_model.issue_data_by_date(self.es,date)
        return result['_source']['summary']

    def update_issue_data(self, param):
        result = issue_management_model.issue_data_by_date(self.es,param['date'])
        summary = result['_source']['summary']
        _id = result['_id']
        filteredSummary = list(filter(lambda x: x['community_num'] != param['num'], summary))
        res = issue_management_model.issue_update_by_num(self.es,_id, filteredSummary)
        if res['result'] == 'updated':
            return 'success'
        else:
            return 'fail'


