from apscheduler.schedulers.background import BackgroundScheduler
from appStockInfo.jobs import KRStocks, USStocks


def taskStockKR():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(KRStocks, 'interval', seconds=5 )

    scheduler.start()


def taskStockUS():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(USStocks, 'interval', seconds=10 )

    scheduler.start()