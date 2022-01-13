from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from datetime import datetime
import json

from apscheduler.schedulers.background import BackgroundScheduler
from appStockInfo.jobs import KRgenData, KRgenPrediction

# Create your views here.
def index(request):
    return HttpResponse("안녕하세요! 주가예측 페이지에 오신것을 환영합니다!")


def generateNewPredictionKR(request):


    if request.method == "POST":

        data = json.loads(request.body)
        print(f'data: {data}')
        context = {
            'result': data,
        }

        scheduler = BackgroundScheduler(timezone="Asia/Seoul")
        scheduler.add_job(KRgenPrediction, 'date',
                          run_date=datetime(2009, 11, 6, 16, 30, 5),
                          args=[],
                          id="KRStocks-Sub"
                          )
        scheduler.add_job(KRgenPrediction, 'cron',
                          hour=hour, minute=min,
                          id="KRStocks")  # 3,19, 01 : xx
        scheduler.start()
        return JsonResponse(context)
    else:
        return render(request, 'appStockPrediction/NewPrediction.html',
                      {'post':'Submit your request!'})
