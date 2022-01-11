from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse  # kkotalk api
from django.views.decorators.csrf import csrf_exempt  # block CSRF attacks
from django.views.decorators.csrf import \
    ensure_csrf_cookie  # https://stackoverflow.com/questions/19598993/csrf-cookie-not-set-django-verification-failed
from django.utils.decorators import method_decorator

import json
import copy

from django.shortcuts import render
from django.views.generic import TemplateView

import decimal
from datetime import datetime, timedelta

from appStockPrediction.models import StockPredictionHistory
from django.db.models import Q

import CommonFunction as CF

import logging
logger = logging.getLogger('my')


@csrf_exempt
def message_lookup(request):
    logger.info(f"appRestAPI - message_lookup")
    answer = ((request.body).decode('utf-8'))
    return_json_str = json.loads(answer)
    utterance = return_json_str['userRequest']['utterance']  # 입력 텍스트 알맹이
    userID = return_json_str['userRequest']['user']['id']  # 입력 텍스트 알맹이
    return_param = return_json_str['action']['detailParams']['종목']["origin"]

    print(f'answer : {answer}')
    print(f'return_json_str : {return_json_str}')
    print(f'utterance : {utterance}')
    print(f'return_param : {return_param}')

    isSuccess = True
    normDate = CF.getNextPredictionDate(datetime.now())
    print(f'normDate : {normDate}')

    if return_param.startswith("종목 "):
        tmpStockName = return_param.replace("종목 ","").strip()
        tmpQuery = StockPredictionHistory.objects.filter(
              (Q(stock_name__stock_name=tmpStockName) | Q(stock_tick__stock_tick=tmpStockName) )
            & Q(prediction_time=normDate)
        )

        try:
            if tmpQuery.exists():
                tmpResult = tmpQuery.first()

                tmpStockName = str(tmpResult.stock_name.stock_name)
                tmpStockCode = str(tmpResult.stock_tick.stock_tick)
                tmpRise = float(tmpResult.value)
                tmpPredict = float(tmpResult.prediction)

                return JsonResponse({
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "simpleText": {
                                    "text": "조회를 성공하였습니다. 결과는 다음과 같습니다."
                                }
                            },
                            {
                                "carousel": {
                                    "type": "itemCard",
                                    "items": [
                                        {
                                            "imageTitle": {
                                                "title": tmpStockName + " : " + tmpStockCode,
                                                "imageUrl": "https://ssl.pstatic.net/imgfinance/chart/item/area/day/" + tmpStockCode + ".png"
                                            },
                                            "itemList": [
                                                {
                                                    "title": f"{'%.3f' % tmpPredict}" + "% 변화",
                                                    "description": str(round(tmpRise)) + " 만큼 변동"
                                                }
                                            ],
                                            "itemListAlignment": "left",
                                            "buttons": [
                                                {
                                                    "label": "네이버 금융 종목 링크",
                                                    "action": "webLink",
                                                    "webLinkUrl": "https://finance.naver.com/item/main.naver?code=" + tmpStockCode
                                                }
                                            ]
                                        }
                                    ]
                                }
                            }
                        ],
                        "quickReplies": [
                            {
                                "messageText": "처음으로",
                                "action": "message",
                                "label": "처음으로"
                            },
                            {
                                'label': str(normDate.strftime("%Y-%m-%d")) + " 예측",
                                'action': 'message',
                                'messageText': '처음으로'
                            },
                        ]
                    }
                })
        except Exception as e:
            print(f'error happened! : {e}')

    return JsonResponse({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "조회 종목 및 코드를 제대로 입력하지 않았거나 없는 코드입니다. 다시 시도해주세요. "
                    }
                },]
            }
        }
    )


@csrf_exempt
def message_getStock20(request, paramNum=20):
    logger.info(f"appRestAPI - message_getStock20")
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
        logger.info(f"appRestAPI - message_getStock20; Exists ORM result")

        replytemplate = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "carousel": {
                            "type":"listCard",
                            "items":[

                            ],
                            "buttons": [
                                {
                                "label": "네이버 금융",
                                "action": "webLink",
                                "webLinkUrl": "https://finance.naver.com/"
                                }
                            ]
                        }

                    }
                ],

                "quickReplies": [
                    {
                        'label': '처음으로',
                        'action': 'message',
                        'messageText': '처음으로'
                    },
                    {
                        'label': str(normDate.strftime("%Y-%m-%d")) + " 예측",
                        'action': 'message',
                        'messageText': '처음으로'
                    },
                ]
            #####
            }
        }

        tmp_replySub = {

                "header" : {"title": "주식 예측 테이블"},
                "items" : []
            }


        tmp_sub = copy.deepcopy(tmp_replySub)
        for idx, data in enumerate(django_filterd):
            if idx % 4 == 0:
                if idx != 0:
                    replytemplate["template"]["outputs"][0]["carousel"]["items"].append(tmp_sub)
                tmp_sub = copy.deepcopy(tmp_replySub)

            tmpStockName = str(data.stock_name)
            tmpStockCode = str(data.stock_tick)
            tmpStockPrediction = float(data.prediction)

            tmp_sub["items"].append({
                "title": tmpStockName  +  "  :  " + tmpStockCode,
                "description": f"{'%.3f' % tmpStockPrediction}" + "% 상승 기대",
                "imageUrl":"https://ssl.pstatic.net/imgfinance/chart/item/area/day/" + tmpStockCode + ".png",
                "link":{
                    "web": "https://finance.naver.com/item/main.naver?code=" + tmpStockCode
                }
            })


        return JsonResponse(replytemplate)


    else:
        logger.info(f"appRestAPI - message_getStock20; No ORM result")
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
def message_getStock20_2(request, paramNum=20):
    logger.info(f"appRestAPI - message_getStock20")
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
        logger.info(f"appRestAPI - message_getStock20; Exists ORM result")
        tmpString = '기업  /  종목번호  /  예상 상승폭\n'
        for data in django_filterd:
            tmpString +=  f"{str(data.stock_name).ljust(11)} -  {str(data.stock_tick)} -> {'%.3f' % float(data.prediction)}\n\n"
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
        logger.info(f"appRestAPI - message_getStock20; No ORM result")
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
