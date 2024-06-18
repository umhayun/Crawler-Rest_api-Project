from flask import Blueprint
from flask_restx import Api

from .admin_api import ns as admin_ns
from .analysis_api import ns as analysis_ns
from .detail_api import ns as detail_ns
from .main_api import ns as main_ns

blueprint = Blueprint("restapi", __name__)

api = Api(blueprint, title="Issue API", version="1.0")

api.add_namespace(admin_ns, path="/admin")
api.add_namespace(main_ns, path="/main")
api.add_namespace(detail_ns, path="/detail")
api.add_namespace(analysis_ns, path="/analysis")
