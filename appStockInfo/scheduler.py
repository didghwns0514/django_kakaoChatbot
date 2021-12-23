from apscheduler.schedulers.background import BackgroundScheduler
from appStockInfo.jobs import serviceKRStocks, serviceUSStocks


def taskStockKR():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(serviceKRStocks, 'cron',
                      hour="3,21", minute="45",
                      id="KRStocks" )
    scheduler.start()


def taskStockUS():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(serviceUSStocks,'cron', hour="16", id="USStocks-1")
    scheduler.add_job(serviceUSStocks,'cron', hour="18", id="USStocks-2")

    scheduler.start()