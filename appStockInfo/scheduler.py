from apscheduler.schedulers.background import BackgroundScheduler
from appStockInfo.jobs import KRStocks, USStocks


def taskStockKR():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(KRStocks, 'cron', hour="2,19", id="KRStocks" )

    scheduler.start()


def taskStockUS():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(USStocks,'cron', hour="17,19", id="USStocks")

    scheduler.start()