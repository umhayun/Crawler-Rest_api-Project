from app.service.main_rank import MainRankService
from flask_restx import Namespace, Resource

ns = Namespace("R-Issue mainboard api")


@ns.route('/weekly', methods=['GET'])
class MainWeekly(Resource):
    @ns.expect()
    def get(self):
        res = MainRankService().get_weekly()
        return res


@ns.route('/daily', methods=['GET'])
class MainDaily(Resource):
    @ns.expect()
    def get(self):
        res = MainRankService().get_daily()
        return res


@ns.route('/detail/<string:id>', methods=['GET'])
class MainDetail(Resource):
    @ns.expect()
    def get(self, id):
        res = MainRankService().get_detail(id)
        return res
