from apscheduler.schedulers.background import BackgroundScheduler
from appStockInfo.jobs import serviceKRStocks, serviceUSStocks


def taskStockKR():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(serviceKRStocks, 'cron', hour="3,19", minute="37", id="KRStocks" )

    scheduler.start()


def taskStockUS():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(serviceUSStocks,'cron', hour="17,19", id="USStocks")

    scheduler.start()