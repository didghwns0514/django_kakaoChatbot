import traceback

from django.db.models.query import QuerySet, Q, F
from appStockInfo.models import (
    StockItem,
    StockTick
)

import ConfigFile as CONF
import CommonFunction as CF

import xgboost
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import explained_variance_score

import datetime
from pytimekr import pytimekr
import pandas as pd

import logging
logger = logging.getLogger('appStockPrediction')

class MainWrapperKR:


    def __init__(self):pass

    def doAction(self):
        pass


    def createPrediction(self) -> [pd.DataFrame, datetime.datetime]:
        """
        train XGBoost and CRUD
        참조 : https://riverzayden.tistory.com/17

        > Main Dataframe columns
        section_integer        total_sum   time_elapsed     open     high      low    close      volume   div    per   pbr       roe   answer    tick
        > Predict Dataframe columns
        section_integer        total_sum   time_elapsed     open     high      low    close      volume   div    per   pbr       roe    tick

        """
        logger.info("MainWrapperKR - createPrediction")
        tmpMainDF, tmpPredDF = self.createPredictionPrep()

        # Convert object types to numeric
        tmpMainDF['section_integer'] = pd.to_numeric(tmpMainDF['section_integer'], errors='coerce')
        tmpMainDF['total_sum']       = pd.to_numeric(tmpMainDF['total_sum'], errors='coerce')
        tmpMainDF['time_elapsed']    = pd.to_numeric(tmpMainDF['time_elapsed'], errors='coerce')
        tmpPredDF['section_integer'] = pd.to_numeric(tmpPredDF['section_integer'], errors='coerce')
        tmpPredDF['total_sum']       = pd.to_numeric(tmpPredDF['total_sum'], errors='coerce')
        tmpPredDF['time_elapsed']    = pd.to_numeric(tmpPredDF['time_elapsed'], errors='coerce')

        # from Main Dataframe
        X, Y = tmpMainDF.loc[:, :'roe'], tmpMainDF.loc[:, 'answer':'answer']
        print(f'X.info() : ')
        X.info()
        print(f'Y.info() : ')
        Y.info()

        # from Prediction Dataframe -> "answer" column is not present here
        PX, PX_indexTick = tmpPredDF.loc[:, :'roe'], tmpPredDF.loc[:, 'tick':]
        print(f'PX.info() : ')
        PX.info()
        print(f'PX_indexTick.info() : ')
        PX_indexTick.info()

        X_train, X_test, y_train, y_test =  train_test_split(X, Y, test_size=0.1)
        xgb_model = xgboost.XGBRegressor(n_estimators=100,
                                         learning_rate=0.08,
                                         gamma=0, subsample=0.75,
                                         colsample_bytree=1,
                                         max_depth=7)

        # Train Model
        xgb_model.fit(X_train, y_train)

        # Plot importance
        xgboost.plot_importance(xgb_model)

        # Prediction for test
        test_predictions = xgb_model.predict(X_test)
        # Score
        r_sq = xgb_model.score(X_train, y_train)
        print(r_sq)
        print(explained_variance_score(test_predictions, y_test))

        # Prediction for real
        real_predictions = xgb_model.predict(PX)

        print(f'real_predictions : \n{real_predictions}')
        print(f'type(real_predictions) : {type(real_predictions)}')
        print(f'type(PY) : {type(PX_indexTick)}')

        PX_indexTick['prediction'] = real_predictions

        # get Date
        try:
            tmplatestDate = StockItem.objects.filter(
                Q(stock_name__stock_tick__stock_isInfoAvailable=True)
            ).order_by('-reg_date').first().reg_date
            latestDate = datetime.datetime(tmplatestDate.year,
                                           tmplatestDate.month,
                                           tmplatestDate.day, hour=CONF.MARKET_TOTAL_FINISH_HOUR)
        except: latestDate = datetime.datetime.now()


        return PX_indexTick, CF.getNextPredictionDate(latestDate)

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
                        callDate:datetime.datetime) -> [pd.DataFrame, pd.DataFrame]:

        globalDataframeMain = CF.generateEmptyDataframe("Main")
        globalDataframePredictions = CF.generateEmptyDataframe("Prediction")

        startDate = CF.getNextPredictionDate(
            callDate - datetime.timedelta(CONF.TOTAL_REQUEST_DATE_LENGTH)
        )
        endDate = callDate

        try:
            tmpQuery = all_Stockitems.filter(
                Q(stock_name__stock_tick__stock_tick=tick)
              & Q(reg_date__range=(startDate, endDate) # get only needed dates
            )

            ).order_by('-reg_date')
            if not tmpQuery.exists():
                raise Exception(f"Empty Database for tick : {tick}")

            previousAnswer = None
            for idx, stockitem in enumerate(tmpQuery):

                tmpInsertData = {
                    'section_integer' : int(stockitem.stock_map_section.section_name.section_integer),
                    'total_sum' : int(stockitem.stock_map_section.total_sum),
                    'time_elapsed' : int(abs(callDate.day - stockitem.reg_date.day)),
                    'open' : stockitem.open,
                    'high' : stockitem.high,
                    'low' : stockitem.low,
                    'close' : stockitem.close,
                    'volume' : stockitem.volume,
                    'div' : stockitem.div,
                    'per' : stockitem.per,
                    'pbr' : stockitem.pbr,
                    'roe' : stockitem.roe,
                    'tick' : str(tick)
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