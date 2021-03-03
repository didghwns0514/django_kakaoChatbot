from apscheduler.schedulers.background import BackgroundScheduler
from BusinessLogic import API_parser

def start():
	scheduler = BackgroundScheduler()
	scheduler.add_job(API_parser.update_stock_list, 'interval', seconds=20)
	scheduler.add_job(API_parser.update_news, 'interval', seconds=10)

	scheduler.start()