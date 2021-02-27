from apscheduler.schedulers.background import BackgroundScheduler
from SeleniumUpdater import API_parser

def start():
	scheduler = BackgroundScheduler()
	scheduler.add_job(API_parser.update_parser_1, 'interval', seconds=20)
	#scheduler.add_job(API_parser.update_parser_test, 'interval', seconds=10)

	scheduler.start()