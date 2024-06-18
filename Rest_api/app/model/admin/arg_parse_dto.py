from flask_restx import Namespace

ns = Namespace("argParser", description="argParser")

elastic_chart_parser = ns.parser()
elastic_chart_parser.add_argument('start', type=str, required=True, help='chart date start')
elastic_chart_parser.add_argument('end', type=str, required=True, help='chart date end')


type_select_parser = ns.parser()

type_select_parser.add_argument('type', type=str, required=False, help='word type')


issue_data_parser = ns.parser()
issue_data_parser.add_argument('date', type=str, required=True, help='auto-ranking job_start_dt')

login_data_parser = ns.parser()
login_data_parser.add_argument('id', type=str, required=True, help='login id')
login_data_parser.add_argument('pw', type=str, required=True, help='login pw')

daily_detail_parser = ns.parser()
daily_detail_parser.add_argument('job_id', type=str, required=False, help='job_id')
