import traceback

from django.db.models.query import QuerySet
from appStockInfo.models import (
    StockItem,
    StockTick
)

import ConfigFile as CONF
import CommonFunction as CF

import datetime
from pytimekr import pytimekr
import pandas as pd

import logging
logger = logging.getLogger('appStockPrediction')

class MainWrapperKR:


    def __init__(self):pass

    def doAction(self):
        pass


    def createPrediction(self):
        """
        train XGBoost and CRUD
        """
        tmpMainDF, tmpPredDF = self.createPredictionPrep()

    def createPredictionPrep(self) -> [pd.DataFrame, pd.DataFrame]:
        """
        create Dataframe and returns total stock dataframe
        for XGBoost prediction
        """
        # global dataframe
        globalDataframeMain = CF.generateEmptyDataframe("Main")
        globalDataframePredictions = CF.generateEmptyDataframe("Prediction")

        globalDate = CF.getNextPredictionDate(datetime.datetime.now())

        # cached stockitems
        all_Stockitems = StockItem.objects.all()

        # work with information provided information
        exist_stocktick = StockTick.objects.filter(
            stock_isInfoAvailable=True
        )

        for tick in exist_stocktick:
            tmpMain, tmpPrediction = self.createDataframe(tick, all_Stockitems=all_Stockitems, callDate=globalDate)
            globalDataframeMain = pd.concat([
                globalDataframeMain, tmpMain
            ])
            globalDataframePredictions = pd.concat([
                globalDataframePredictions, tmpPrediction
            ])

        return globalDataframeMain, globalDataframePredictions


    def createDataframe(self, tick,
                        all_Stockitems:QuerySet,
                        callDate:datetime.date) -> [pd.DataFrame, pd.DataFrame]:

        globalDataframeMain = CF.generateEmptyDataframe("Main")
        globalDataframePredictions = CF.generateEmptyDataframe("Prediction")

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



# active information columns only selected
# exist_stockitems = StockItem.objects.filter(
#     stock_map_section__stock_tick__stock_isInfoAvailable=True
# ).values_list(flat=True)