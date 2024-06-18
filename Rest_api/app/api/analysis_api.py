import logging
import app.model.analysis_dto as analysis_dto
from app.service.analysis import AnalysisService
from flask import request, jsonify, make_response
from flask_restx import Namespace, Resource, fields

# (job_id, user_id, running_step, louvain_resolution,
# search_start_date,search_end_date, include_keyword, exclude_keyword, doc_id, count)
ns = Namespace("Analysis api")
analysis_status_fields = ns.model('analysis', {  # Model 객체 생성 # 4대강 /politic
    'job_id': fields.String(description='AnalysisStatus', required=True, example="job_id"),
    'user_id': fields.String(description='AnalysisStatus', required=True, example="user_id"),
    'analysis_name': fields.String(description='AnalysisStatus', required=True, example="analysis_name"),
    'media': fields.String(description='AnalysisStatus', required=True, example="네이버_블로그,네이버_카페"),
    'louvain_resolution': fields.String(description='AnalysisStatus', required=True, example="0.88"),
    'search_start_date': fields.String(description='AnalysisStatus', required=True, example="2023-12-12 00:00:00"),
    'search_end_date': fields.String(description='AnalysisStatus', required=True, example="2023-12-12 00:00:00"),
    'incexc_keyword': fields.String(description='AnalysisStatus', required=True, example="부상"),
    'count': fields.String(description='AnalysisStatus', required=True, example=0)
})
analysis_delete_json = ns.model('delete', {
    'job_id': fields.String(description='AnalysisStatus', required=True, example="job_id")
})


@ns.route('/count', methods=['GET'])
class Analysis(Resource):
    @ns.expect(analysis_dto.analysis_parser)
    def get(self):
        params = analysis_dto.analysis_parser.parse_args()
        res = AnalysisService().get_analysis(params['include'], params['exclude'], params['media'], params['start'], params['end'])
        return res


@ns.route('/list', methods=['GET', 'PUT', 'DELETE'])
class AnalysisStatus(Resource):
    # 분석 list select
    @ns.expect()
    def get(self):
        res = AnalysisService().get_data()
        return res

    @ns.expect(analysis_status_fields)
    def put(self):
        data = request.get_json()
        res = AnalysisService().insert_data(data)
        return res

    @ns.expect(analysis_delete_json)
    def delete(self):
        try:
            request_param = request.get_json(force=True)

            # JSON key check
            required_keys = ["job_id"]
            if not all(key in request_param for key in required_keys):
                return make_response(jsonify({'message': "Key not found in JSON. Key: 'job_id"}), 400)

            # json parse
            job_id = request_param["job_id"]

            # Make sure request is existed
            if not job_id:
                return make_response(jsonify({"message": "'job_id' should not be empty value."}), 400)

            response = AnalysisService().delete_analysis_data(job_id)
            if response != 0:
                return make_response(jsonify({"response": "delete success"}), 200)
            else:
                return make_response(jsonify({"response": "delete fail"}), 400)

        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            logging.error(f'delete analysis error: ({error_type}){error_message}')
            return {'error': "(" + error_type + ")" + error_message}, 400


@ns.route('/start/<string:job_id>', methods=['GET'])
class AnalysisStart(Resource):
    def get(self, job_id):
        res = AnalysisService().analysis_start(job_id)
        return res
