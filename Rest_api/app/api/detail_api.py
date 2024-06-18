
import app.model.admin.arg_parse_dto as daily_dto
from app.service.analysis_detail import AnalysisDetailService
from app.service.main_detail import MainDetailService
from flask_restx import Namespace, Resource

ns = Namespace("Issue detail common api")


@ns.route('/summary/<string:page>/<string:id>', methods=['GET'])
class DetailSummary(Resource):
    @ns.expect(daily_dto.daily_detail_parser)
    def get(self, id, page):
        params = daily_dto.daily_detail_parser.parse_args()
        if page == 'main' or page == 'daily':
            res = MainDetailService(params['job_id']).get_summary(id)
        elif page == 'analysis':
            res = AnalysisDetailService().get_summary(id)

        return res


@ns.route('/community/<string:page>/<string:id>', methods=['GET'])
class DetailCommunity(Resource):
    @ns.expect(daily_dto.daily_detail_parser)
    def get(self, id, page):
        params = daily_dto.daily_detail_parser.parse_args()
        if page == 'main' or page == 'daily':
            res = MainDetailService(params['job_id']).get_community(id)
        elif page == 'analysis':
            res = AnalysisDetailService().get_community(id)

        return res


@ns.route('/mediacount/<string:page>/<string:id>', methods=['GET'])
class DetailMediaCount(Resource):
    @ns.expect(daily_dto.daily_detail_parser)
    def get(self, id, page):
        params = daily_dto.daily_detail_parser.parse_args()
        if page == 'main' or page == 'daily':
            res = MainDetailService(params['job_id']).get_media_count(id)
        elif page == 'analysis':
            res = AnalysisDetailService().get_media_count(id)
        return res


@ns.route('/issueprocess/<string:page>/<string:id>', methods=['GET'])
class DetailIssueProcess(Resource):
    @ns.expect(daily_dto.daily_detail_parser)
    def get(self, id, page):
        params = daily_dto.daily_detail_parser.parse_args()
        if page == 'main' or page == 'daily':
            res = MainDetailService(params['job_id']).get_issue_process(id)
        elif page == 'analysis':
            res = AnalysisDetailService().get_issue_process(id)
        return res


@ns.route('/wordcloud/<string:page>/<string:id>', methods=['GET'])
class DetailWordCloud(Resource):
    @ns.expect(daily_dto.daily_detail_parser)
    def get(self, id, page):
        params = daily_dto.daily_detail_parser.parse_args()
        if page == 'main' or page == 'daily':
            res = MainDetailService(params['job_id']).get_wordcloud(id)
        elif page == 'analysis':
            res = AnalysisDetailService().get_wordcloud(id)
        return res


@ns.route('/sentigraph/<string:page>/<string:id>', methods=['GET'])
class DetailSentiGraph(Resource):
    @ns.expect(daily_dto.daily_detail_parser)
    def get(self, id, page):
        params = daily_dto.daily_detail_parser.parse_args()
        if page == 'main' or page == 'daily':
            res = MainDetailService(params['job_id']).get_senti_graph(id)
        elif page == 'analysis':
            res = AnalysisDetailService().get_senti_graph(id)
        return res
