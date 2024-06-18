from flask_restx import Namespace

ns = Namespace("analysisParser", description="analysisParser")

analysis_parser = ns.parser()
analysis_parser.add_argument('include', type=str, required=True, help='include keyword')
analysis_parser.add_argument('exclude', type=str, required=False, help='exclude keyword')
analysis_parser.add_argument('media', type=str, required=True, help='search media')
analysis_parser.add_argument('start', type=str, required=True, help='chart date start')
analysis_parser.add_argument('end', type=str, required=True, help='chart date end')
