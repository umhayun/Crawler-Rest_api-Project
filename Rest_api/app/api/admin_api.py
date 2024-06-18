
import app.model.admin.arg_parse_dto as arg_parse_dto
from app.service.admin.crawler_state import CrawlerStateService
from app.service.admin.data_collection import DataCollectionService as dc
from app.service.admin.issue_management import IssueManagementService as im
from app.service.admin.manual_crawling import ManualCrawlingService
from app.service.admin.related_word import RelatedWordService
from app.service.admin.senti_keyword import SentiKeywordService
from app.service.admin.special_word import SpecialWordService
from app.service.admin.user_management import UserService
from flask import request
from flask_restx import Namespace, Resource, fields

ns = Namespace("Issue admin api")

admin_fields = ns.model('special', {  # Model 객체 생성 # 4대강 /politic
    'word': fields.String(description='SpecialWord', required=True, example="4대강"),
    'type': fields.String(description='SpecialWord', required=True, example="politic"),
    'remove': fields.String(description='SpecialWord', required=True, example="Y"),
})
senti_fields = ns.model('word', {  # Model 객체 생성 # 4대강 /politic
    'category': fields.String(description='SentiKeyword', required=True, example="test"),
    'keyword': fields.String(description='SentiKeyword', required=True, example="test")
})
user_fields = ns.model('user', {  # Model 객체 생성 # 4대강 /politic
    'id': fields.String(description='User', required=True, example="testid"),
    'password': fields.String(description='User', required=True, example="testpw"),
    'name': fields.String(description='User', required=True, example="test"),
    'department': fields.String(description='User', required=True, example="testdept"),
    'tel': fields.String(description='User', required=True, example="01000000000"),
    'email': fields.String(description='User', required=True, example="test@email.com")
})
issue_fields = ns.model('issue', {
    'date': fields.String(description='Issue', required=True, example='2023-11-23T14:14:15.156Z'),
    'num': fields.String(description='Issue', required=True, example='2')
})
related_fields = ns.model('word', {  # Model 객체 생성 # 4대강 /politic
    'category': fields.String(description='RelatedKeyword', required=True, example="test"),
    'keyword': fields.String(description='RelatedKeyword', required=True, example="test")
})
crawler_fields = ns.model('crawler', {
    'keyword': fields.String(description='Crawler', required=True, example='사망,숨지,숨져,숨진'),
    'crawler_name': fields.String(description='Crawler', required=True, example='naver_blog'),
    'start_date': fields.String(description='crawler', required=True, example='2023-12-01 00:00:00'),
    'end_date': fields.String(description='Crawler', required=True, example='2023-12-01 23:59:59')
})


@ns.route('/datacollection/date', methods=['GET'])
class DataCollectionDate(Resource):
    # 날짜별 총개수
    @ns.expect(arg_parse_dto.elastic_chart_parser)
    def get(self):
        params = arg_parse_dto.elastic_chart_parser.parse_args()
        result = dc().search_date(params['start'], params['end'])
        return result


@ns.route('/datacollection/media', methods=['GET'])
class DataCollectionMedia(Resource):
    # 미디어별 총개수
    @ns.expect()
    def get(self):
        result = dc().search_media()
        return result


@ns.route('/crawlerstate', methods=['GET'])
class Crawlerstate(Resource):
    @ns.expect()
    def get(self):
        res = CrawlerStateService().get_data()
        return res


@ns.route('/specialword', methods=['GET', 'PUT'])
class SpecialWord(Resource):
    # 조회
    @ns.expect(arg_parse_dto.type_select_parser)
    def get(self):
        params = arg_parse_dto.type_select_parser.parse_args()
        res = SpecialWordService().select_data(params['type'])
        return res
    # 등록

    @ns.expect(admin_fields)
    def put(self):
        data = request.get_json()
        result = SpecialWordService().insert_data(data)
        return result


@ns.route('/specialword/<string:word>', methods=['GET', 'POST', 'DELETE'])
class SpecialWordChange(Resource):
    # 특정 데이터 출력
    @ns.expect()
    def get(self, word):
        result = SpecialWordService().select_one(word)
        return result

    # 수정
    @ns.expect(admin_fields)
    def post(self, word):
        new_data = request.get_json()
        result = SpecialWordService().update_data(word, new_data)
        return result

    # 삭제
    @ns.expect()
    def delete(self, word):
        res = SpecialWordService().delete_data(word)
        return res


@ns.route('/sentikeyword', methods=['GET', 'PUT'])
class SentiKeyword(Resource):

    @ns.expect(arg_parse_dto.type_select_parser)
    def get(self):
        params = arg_parse_dto.type_select_parser.parse_args()
        res = SentiKeywordService().select_data(params['type'])
        return res

    @ns.expect(senti_fields)
    def put(self):
        data = request.get_json()
        res = SentiKeywordService().insert_data(data)
        return res


@ns.route('/sentikeyword/<string:category>/<string:keyword>', methods=['GET', 'POST', 'DELETE'])
class SentiKeywordChange(Resource):

    def get(self, category, keyword):
        res = SentiKeywordService().select_one_data(category, keyword)
        return res

    @ns.expect(senti_fields)
    def post(self, category, keyword):
        data = request.get_json()
        res = SentiKeywordService().update_data(category, keyword, data)
        return res

    def delete(self, category, keyword):
        res = SentiKeywordService().delete_data(category, keyword)
        return res


@ns.route('/sentikeyword/types', methods=['GET'])
class SentiKeywordTypes(Resource):
    def get(self):
        res = SentiKeywordService().select_types()
        return res


@ns.route('/user', methods=['GET', 'PUT'])
class UserManagement(Resource):

    def get(self):
        res = UserService().select_data()
        return res

    @ns.expect(user_fields)
    def put(self):
        data = request.get_json()
        res = UserService().insert_data(data)
        return res


@ns.route('/user/<string:id>', methods=['GET', 'POST', 'DELETE'])
class UserManagementChange(Resource):
    # 특정 데이터 출력
    @ns.expect()
    def get(self, id):
        result = UserService().select_one_data(id)
        return result

    # 수정
    @ns.expect(user_fields)
    def post(self, id):
        new_data = request.get_json()
        result = UserService().update_data(id, new_data)
        return result

    # 삭제
    @ns.expect()
    def delete(self, id):
        res = UserService().delete_data(id)
        return res


@ns.route('/login', methods=['GET'])
class Login(Resource):
    @ns.expect(arg_parse_dto.login_data_parser)
    def get(self):
        params = arg_parse_dto.login_data_parser.parse_args()
        result = UserService().check_login(params['id'], params['pw'])
        return result


@ns.route('/issue/dates', methods=['GET'])
class IssueDateList(Resource):
    @ns.expect()
    def get(self):
        res = im().search_issue_dates()
        return res


@ns.route('/issue/data', methods=['GET', 'POST'])
class IssueManagement(Resource):
    @ns.expect(arg_parse_dto.issue_data_parser)
    def get(self):
        params = arg_parse_dto.issue_data_parser.parse_args()
        res = im().search_issue_data(params['date'])
        return res

    @ns.expect(issue_fields)
    def post(self):
        new_data = request.get_json()
        res = im().update_issue_data(new_data)
        return res


@ns.route('/relatedword', methods=['GET', 'PUT'])
class RelatedKeyword(Resource):

    @ns.expect(arg_parse_dto.type_select_parser)
    def get(self):
        params = arg_parse_dto.type_select_parser.parse_args()
        res = RelatedWordService().select_data(params['type'])
        return res

    @ns.expect(related_fields)
    def put(self):
        data = request.get_json()
        res = RelatedWordService().insert_data(data)
        return res


@ns.route('/relatedword/<string:category>/<string:keyword>', methods=['GET', 'POST', 'DELETE'])
class RelatedKeywordChange(Resource):

    def get(self, category, keyword):
        res = RelatedWordService().select_one_data(category, keyword)
        return res

    @ns.expect(related_fields)
    def post(self, category, keyword):
        data = request.get_json()
        res = RelatedWordService().update_data(category, keyword, data)
        return res

    def delete(self, category, keyword):
        res = RelatedWordService().delete_data(category, keyword)
        return res


@ns.route('/relatedword/types', methods=['GET'])
class RelatedKeywordTypes(Resource):
    def get(self):
        res = RelatedWordService().select_types()
        return res


@ns.route('/manualcrawling', methods=['GET', 'PUT'])
class Crawlerstate(Resource):
    @ns.expect()
    def get(self):
        res = ManualCrawlingService().get_data()
        return res

    @ns.expect(crawler_fields)
    def put(self):
        data = request.get_json()
        res = ManualCrawlingService().insert_data(data)
        return res
