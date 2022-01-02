from apscheduler.schedulers.background import BackgroundScheduler
from appStockInfo.jobs import serviceKRStocks, serviceUSStocks


def taskStockKR():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(serviceKRStocks, 'cron',
                      hour="3,20", minute="44",
                      id="KRStocks" ) # 3,19 : xx
    scheduler.start()


def taskStockUS():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(serviceUSStocks,'cron', hour="16", id="USStocks-1")
    scheduler.add_job(serviceUSStocks,'cron', hour="18", id="USStocks-2")

    scheduler.start()