from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse  # kkotalk api
from django.views.decorators.csrf import csrf_exempt  # block CSRF attacks
from django.views.decorators.csrf import \
    ensure_csrf_cookie  # https://stackoverflow.com/questions/19598993/csrf-cookie-not-set-django-verification-failed
from django.utils.decorators import method_decorator

import json

from django.shortcuts import render
from django.views.generic import TemplateView

import decimal
from datetime import datetime, timedelta

from appStockPrediction.models import StockPredictionHistory
from django.db.models import Q

import CommonFunction as CF


@csrf_exempt
def message_getStock20(request, paramNum=20):
    print(f'called!!')
    answer = ((request.body).decode('utf-8'))
    return_json_str = json.loads(answer)
    return_str = return_json_str['userRequest']['utterance']  # 입력 텍스트 알맹이
    print(f'return_json_str : {return_json_str}')
    print(f'return_str : {return_str}')


    # @ Query performed
    normDate = CF.getNextPredictionDate(datetime.now())
    print(f'normDate : {normDate}')
    djangoORM = StockPredictionHistory.objects.filter(
        Q(prediction_time__gte=normDate)
    ).order_by('-prediction')  # 내림차순 ,desc order
    django_filterd = [data for n, data in enumerate(djangoORM)
                      if n <= paramNum if data.prediction > 0  # check price ratio constraints
                    ]

    if django_filterd:  # ORM exists
        tmpString = ''
        for data in django_filterd:
            tmpString +=  f"{('%10s' % str(data.stock_name))} - " \
                          f"{str(data.stock_tick)} -> {'%.3f' % float(data.prediction)}\n"
        str([(data.stock_name, data.prediction) for data in django_filterd])
        return JsonResponse({
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': tmpString
                    }
                }],
                'quickReplies': [{
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        })
    else:
        return JsonResponse({
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': "추천할 종목이 없습니다..."
                    }
                }],
                'quickReplies': [{
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        })


@csrf_exempt
def message_getStock20_1(request):
    print(f'called!!')
    answer = ((request.body).decode('utf-8'))
    return_json_str = json.loads(answer)
    return_str = return_json_str['userRequest']['utterance']  # 입력 텍스트 알맹이
    print(f'return_json_str : {return_json_str}')
    print(f'return_str : {return_str}')

    return_param = return_json_str['action']['params']['종목군']
    if return_param in ['코스닥', '코스피']:
        Q_filter = Q(source__iexact=return_param)
    elif return_param == '무관':
        Q_filter = Q()
    else:
        raise ValueError('wrong param in message stock')

    # @ Query performed
    djangoORM = StockListData.objects.filter(Q_filter).order_by('-price_ratio')  # 내림차순 ,desc order
    django_filterd = [data for n, data in enumerate(djangoORM)
                      if n <= 10 if data.price_ratio > 0  # check price ratio constraints
                      if check_timeStamp(data.timestamp)]

    if django_filterd:  # ORM exists
        return JsonResponse({
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': f'{str([(data.name, data.price_ratio) for data in django_filterd])}'
                    }
                }],
                'quickReplies': [{
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        })
    else:
        return JsonResponse({
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': "추천할 종목이 없습니다..."
                    }
                }],
                'quickReplies': [{
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        })

@csrf_exempt
def message_merge(request):
    answer = ((request.body).decode('utf-8'))
    return_json_str = json.loads(answer)
    return_str = return_json_str['userRequest']['utterance']  # 입력 텍스트 알맹이

    if return_str == '테스트':
        return JsonResponse({
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': "테스트 성공입니다."
                    }
                }],
                'quickReplies': [{
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        })
    else:
        return JsonResponse({
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': "응답할 수 없습니다."
                    }
                }],
                'quickReplies': [{
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        })


# https://i.kakao.com/docs/skill-build#%EC%8A%A4%ED%82%AC-%EC%84%9C%EB%B2%84-%EC%84%B8%ED%8C%85
@csrf_exempt
def message_news(request):
    # request.body -> json payload
    # https://dev-dain.tistory.com/6?category=816329

    answer = ((request.body).decode('utf-8'))
    return_json_str = json.loads(answer)
    return_str = return_json_str['userRequest']['utterance']  # 입력 텍스트 알맹이

    if return_str == '테스트':
        return JsonResponse({
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': "테스트 성공입니다."
                    }
                }],
                'quickReplies': [{
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        })
    else:
        return JsonResponse({
            'version': "2.0",
            'template': {
                'outputs': [{
                    'simpleText': {
                        'text': "응답할 수 없습니다."
                    }
                }],
                'quickReplies': [{
                    'label': '처음으로',
                    'action': 'message',
                    'messageText': '처음으로'
                }]
            }
        })
