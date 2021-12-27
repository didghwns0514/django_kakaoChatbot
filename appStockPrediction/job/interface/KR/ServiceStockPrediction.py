import traceback

from django.db.models.query import QuerySet
from appStockInfo.models import (
    StockItem,
    StockTick
)

import ConfigFile as CF

import datetime
from pytimekr import pytimekr
import pandas as pd

import logging
logger = logging.getLogger('my')

class MainWrapperKR:


    def __init__(self):pass

    def doAction(self):
        pass


    def createPrediction(self):
        """
        train XGBoost and CRUD
        """
        pass

    def createPredictionPrep(self):
        """
        create Dataframe and returns total stock dataframe
        for XGBoost prediction
        """
        # global dataframe
        column_names = [
            "section_integer",
            "total_sum",
            "time_elapsed",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "div",
            "per",
            "pbr",
            "roe",
            "answer"
        ]
        globalDataframeMain = pd.DataFrame(
            columns=column_names
        )
        globalDataframePredictions = pd.DataFrame(
            columns=column_names[:len(column_names)-1] # "answer" removed
        )
        globalDate = getNextPredictionDate(datetime.datetime.now())

        # cached stockitems
        all_Stockitems = StockItem.objects.all()

        # work with information provided information
        exist_stocktick = StockTick.objects.filter(
            stock_isInfoAvailable=True
        )

        for tick in exist_stocktick:
            tmpMain, tmpPrediction = self.createDataframe(tick,
                                     column_names=column_names,
                                     all_Stockitems=all_Stockitems,
                                     callDate=globalDate
                                 )
            globalDataframeMain = pd.concat([
                globalDataframeMain, tmpMain
            ])
            globalDataframePredictions = pd.concat([
                globalDataframePredictions, tmpPrediction
            ])


    def createDataframe(self, tick,
                        column_names:list,
                        all_Stockitems:QuerySet,
                        callDate:datetime.date):

        globalDataframeMain:pd.DataFrame = pd.DataFrame(columns=column_names)
        globalDataframePredictions:pd.DataFrame = pd.DataFrame(columns=column_names[:len(column_names) - 1])

        try:
            tmpQuery = all_Stockitems.filter(stock_name__stock_tick__stock_tick=tick).order_by('-reg_date')
            if not tmpQuery.exists():
                raise Exception(f"Empty Database for tick : {tick}")

            previousAnswer = None
            for idx, stockitem in enumerate(tmpQuery):

                tmpInsertData = {
                    'section_integer' : stockitem.stock_map_section.section_name.section_integer,
                    'total_sum' : stockitem.stock_map_section.total_sum,
                    'time_elapsed' : int(abs(callDate.day - stockitem.reg_date.day)),
                    'open' : stockitem.open,
                    'high' : stockitem.high,
                    'low' : stockitem.low,
                    'close' : stockitem.close,
                    'volume' : stockitem.volume,
                    'div' : stockitem.div,
                    'per' : stockitem.per,
                    'pbr' : stockitem.pbr,
                    'roe' : stockitem.roe
                }
                if idx == 0:  # first index which needs predictions
                    globalDataframePredictions = globalDataframePredictions.append(
                        tmpInsertData, ignore_index=True
                    )
                    previousAnswer = stockitem.close
                else:
                    tmpInsertData["answer"] = previousAnswer
                    globalDataframeMain = globalDataframeMain.append(
                        tmpInsertData, ignore_index=True
                    )
                    previousAnswer = stockitem.close

        except Exception as e:
            logger.warning(f"appStockPrediction - MainWrapperKR - createDataframe; {e}")

        finally:
            return globalDataframeMain, globalDataframePredictions

def getNextPredictionDate(callDate:datetime.date):
    # https://velog.io/@vanang7/Python으로-공휴일-리스트를-만들자
    for _ in range(CF.TOTAL_RETRY_FOR_FETCH_FAIL):
        kr_holidays = pytimekr.holidays()
        if kr_holidays: break
    else: logger.critical('getNextPredictionDate; Date generation failed')

    if 16 < callDate.hour < 24:
        callDate += datetime.timedelta(days=1)

    callDateFiltered = datetime.datetime(
        callDate.year, callDate.month, callDate.day
    )

    # 0, 1, 2, 3, 4, 5, 6
    # 월, 화, 수, 목, 금, 토, 일
    counter = 0
    while ( callDateFiltered.weekday() in [5, 6]) or callDateFiltered in kr_holidays or \
        counter >= 7:
        callDateFiltered += datetime.timedelta(days=1)
        counter += 1

    return callDateFiltered

# active information columns only selected
# exist_stockitems = StockItem.objects.filter(
#     stock_map_section__stock_tick__stock_isInfoAvailable=True
# ).values_list(flat=True)