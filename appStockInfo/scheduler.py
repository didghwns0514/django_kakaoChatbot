from apscheduler.schedulers.background import BackgroundScheduler
from appStockInfo.jobs import JobDatetime1, JobDatetime2


def taskStockKR():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(JobDatetime1, 'interval', seconds=5 )

    scheduler.start()


def taskStockUS():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(JobDatetime2, 'interval', seconds=10 )

    scheduler.start()