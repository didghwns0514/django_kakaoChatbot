from apscheduler.schedulers.background import BackgroundScheduler
from appStockInfo.jobs import serviceKRStocks, serviceUSStocks
import StockManager.subSettings as CONFI
import os

import logging
logger = logging.getLogger('appStockInfo')

def taskStockKR():

    if not CONFI.IS_MAIN_SERVER:
        if CONFI.DEBUG:
            hour = str(os.environ.get('HOUR'))
            min = str(os.environ.get('MIN'))
            logger.info("appStockInfo - taskStockKR; DEBUG true; not a main server/get data")
        else:
            hour = "3,19"
            min = "01"
            logger.info("appStockInfo - taskStockKR; DEBUG false; not a main server/get data")

        scheduler = BackgroundScheduler(timezone="Asia/Seoul")
        scheduler.add_job(serviceKRStocks, 'cron',
                          hour=hour, minute=min,
                          id="KRStocks" ) # 3,19, 01 : xx
        scheduler.start()

    else:
        logger.info("appStockInfo - taskStockKR; is a main server/dont get data")



def taskStockUS():
    logger.info("appStockInfo - taskStockUS; not a main server/get data")
    if not CONFI.IS_MAIN_SERVER:
        scheduler = BackgroundScheduler(timezone="Asia/Seoul")
        scheduler.add_job(serviceUSStocks,'cron', hour="16", id="USStocks-1")
        scheduler.add_job(serviceUSStocks,'cron', hour="18", id="USStocks-2")

        scheduler.start()
    else:
        logger.info("appStockInfo - taskStockUS; is a main server/dont get data")
