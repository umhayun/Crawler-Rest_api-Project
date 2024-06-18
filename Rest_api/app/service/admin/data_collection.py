from app.model.admin import data_collection_model
from utils.els_utils import ELSUtils


class DataCollectionService:
    def __init__(self):
        self.es = ELSUtils().getConn()

    def search_date(self, start: str, end: str):
        datacollection_dic = {}
        com_date = data_collection_model.comment_total_by_date(self.es, start, end)
        post_date = data_collection_model.post_total_by_date(self.es, start, end)
        datacollection_dic['comment_cnt_by_date'] = com_date
        datacollection_dic['post_cnt_by_date'] = post_date
        return datacollection_dic

    def search_media(self):
        datacollection_dic = {}
        com_media = data_collection_model.comment_total_by_media(self.es)
        post_media = data_collection_model.post_total_by_media(self.es)
        datacollection_dic['comment_cnt_by_media'] = com_media
        datacollection_dic['post_cnt_by_media'] = post_media
        return datacollection_dic
