import traceback

from django.db.models.query import QuerySet, Q, F
from appStockInfo.models import (
    StockItem,
    StockTick,
    StockItemListName
)
from appStockPrediction.models import (
    StockPredictionHistory
)

import ConfigFile as CONF
import CommonFunction as CF

import numpy as np
import xgboost
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
"""
score in sklearn : https://scikit-learn.org/stable/modules/classes.html#sklearn-metrics-metrics

"""
from sklearn.metrics import explained_variance_score

import datetime
import pandas as pd

import logging
logger = logging.getLogger('appStockPrediction')


class MainWrapperKR:


    def __init__(self):pass

    def doAction(self):

        self.createStockPredictionHistory(datetime.datetime.now())


    def createStockPredictionHistory(self, callDate:datetime.datetime):
        """
        StockPrediction CRUD
        """
        logger.info("MainWrapperKR - createStockPredictionHistory")

        predictionDF, predictionDay = self.createPrediction(callDate=callDate)
        tmpPredictionDayFilter = StockPredictionHistory.objects.all()
        filter_1 = []

        for idx, row in predictionDF.iterrows():
            try:
                tmpTick = row['tick']
                tmpPrediction = row['prediction']
                tmpClose = row['close']

                # for CRUD
                if not tmpPredictionDayFilter.filter(
                      Q(prediction_time=predictionDay)
                    & Q(stock_tick=tmpTick)
                ).exists():

                    tmp_StockTick = StockTick.objects.get(
                        stock_tick=tmpTick
                    )

                    tmp_StockName = StockItemListName.objects.get(
                        stock_tick__stock_tick=tmpTick
                    )

                    filter_1.append(
                        StockPredictionHistory(
                            stock_name=tmp_StockName,
                            stock_tick=tmp_StockTick,
                            prediction_time=predictionDay,
                            prediction_percent=((tmpPrediction - tmpClose) / tmpClose) * 100,
                            value=tmpPrediction
                        )
                    )
            except Exception as e:
                logger.info(f"MainWrapperKR - createStockPredictionHistory; Error happened : {e}")
                traceback.print_exc()

        # Bulk create
        StockPredictionHistory.objects.bulk_create(
            filter_1
        )

        logger.info(f"MainWrapperKR - createStockPredictionHistory; Total new objects : {len(filter_1)}")



    def createPrediction(self,
                         callDate:datetime.datetime,
                         tmpMainDF=None,tmpPredDF=None,tmpWindowDF=None
                         ) -> [pd.DataFrame, datetime.datetime]:
        """
        train XGBoost and return Result
        참조 : https://riverzayden.tistory.com/17

        > Main Dataframe columns
        section_integer        total_sum   time_elapsed     open     high      low    close      volume   div    per   pbr       roe   answer    tick
        > Predict Dataframe columns
        section_integer        total_sum   time_elapsed     open     high      low    close      volume   div    per   pbr       roe    tick

        """
        logger.info("MainWrapperKR - createPrediction")
        if not isinstance(tmpMainDF,pd.DataFrame) or \
                not isinstance(tmpPredDF, pd.DataFrame) or \
                not isinstance(tmpWindowDF, pd.DataFrame):
            tmpMainDF, tmpPredDF, tmpWindowDF = self.createPredictionPrep(callDate=callDate)

        # Convert object types to numeric
        tmpMainDF['section_integer'] = pd.to_numeric(tmpMainDF['section_integer'], errors='coerce')
        tmpMainDF['total_sum']       = pd.to_numeric(tmpMainDF['total_sum'], errors='coerce')
        tmpMainDF['time_elapsed']    = pd.to_numeric(tmpMainDF['time_elapsed'], errors='coerce')
        tmpPredDF['section_integer'] = pd.to_numeric(tmpPredDF['section_integer'], errors='coerce')
        tmpPredDF['total_sum']       = pd.to_numeric(tmpPredDF['total_sum'], errors='coerce')
        tmpPredDF['time_elapsed']    = pd.to_numeric(tmpPredDF['time_elapsed'], errors='coerce')

        # print(f'tmpMainDF')
        # print(f'len(tmpMainDF) : {len(tmpMainDF)}')
        # tmpMainDF.info()
        # tmpMainDF.head(3)
        # print(f'tmpPredDF')
        # print(f'len(tmpPredDF) : {len(tmpPredDF)}')
        # tmpPredDF.info()
        # tmpPredDF.head(3)

        # from Main Dataframe
        X, Y = tmpMainDF.loc[:, :'roe'], tmpMainDF.loc[:, 'answer':'answer']

        # from Prediction Dataframe -> "answer" column is not present here
        PX, PX_indexTick = tmpPredDF.loc[:, :'roe'], tmpPredDF.loc[:, 'tick':]

        """
        Param explained : https://towardsdatascience.com/a-guide-to-xgboost-hyperparameters-87980c7f44a9
        Hyper and more : https://xgboost.readthedocs.io/en/latest/parameter.html
    
        """
        X_train, X_test, y_train, y_test =  train_test_split(X, Y, test_size=0.2)
        xgb_model = xgboost.XGBRegressor(n_estimators=100,
                                         subsample=0.75,
                                         learning_rate=0.3,
                                         gamma=0,
                                         colsample_bytree=1,
                                         max_depth=10,
                                         eval_metric="mape")

        # Train Model
        xgb_model.fit(X_train, y_train)

        # Plot importance
        # UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
        # terminating with uncaught exception of type NSException
        #xgboost.plot_importance(xgb_model)

        # Prediction for test
        test_predictions = xgb_model.predict(X_test)
        # Scores
        # 1)
        test_score = explained_variance_score(test_predictions, y_test)
        logger.info(f"MainWrapperKR - createPrediction; Prediction score test : {test_score}")
        # 2)
        train_score = xgb_model.score(X_train, y_train)
        logger.info(f"MainWrapperKR - createPrediction; Prediction score train : {train_score}")
        # 3)
        mpe = myMPE(test_predictions, y_test.to_numpy())
        logger.info(f"MainWrapperKR - createPrediction; Prediction score train/mpe : {mpe}")

        ## print
        print(f'test_score : {test_score}')
        print(f'train_score : {train_score}')
        print(f'mpe : {mpe}')

        # Prediction for real
        real_predictions = xgb_model.predict(PX)


        PX_indexTick['prediction'] = real_predictions.tolist()
        PX_indexTick['close'] = PX['close']

        # get Date
        try:
            tmplatest = StockItem.objects.filter(
                Q(stock_name__stock_tick__stock_isInfoAvailable=True)
            ).order_by('-reg_date').first()

            tmplatestDate = tmplatest.reg_date

            latestDate = datetime.datetime(tmplatestDate.year,
                                           tmplatestDate.month,
                                           tmplatestDate.day, hour=CONF.MARKET_TOTAL_FINISH_HOUR)
        except: latestDate = datetime.datetime.now()


        return PX_indexTick, CF.getNextPredictionDate(latestDate)


    def createPredictionPrep(self, callDate:datetime.datetime) -> [pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        create Dataframe and returns total stock dataframe
        for XGBoost prediction
        """
        logger.info("MainWrapperKR - createPredictionPrep")

        # global dataframe
        globalDataframeMain = CF.generateEmptyDataframe("Main")
        globalDataframePredictions = CF.generateEmptyDataframe("Prediction")
        globalDataframeWindow = CF.generateEmptyDataframe("Window")

        globalDate = CF.getNextPredictionDate(callDate)

        # cached stockitems
        all_Stockitems = StockItem.objects.all()

        # work with information provided information
        exist_stocktick = StockTick.objects.filter(
            stock_isInfoAvailable=True
        )

        for idx, tick in enumerate(exist_stocktick):
            tmpMain, tmpPrediction, tmpWindow = self.createDataframe(tick,
                                                          all_Stockitems=all_Stockitems,
                                                          callDate=globalDate,
                                                          countIndex=idx)
            globalDataframeMain = pd.concat([
                globalDataframeMain, tmpMain
            ])
            globalDataframePredictions = pd.concat([
                globalDataframePredictions, tmpPrediction
            ])
            globalDataframeWindow = pd.concat([
                globalDataframeWindow, tmpWindow
            ])

        return globalDataframeMain, globalDataframePredictions, globalDataframeWindow


    def createDataframe(self, tick,
                        all_Stockitems:QuerySet,
                        callDate:datetime.datetime,
                        countIndex=0) -> [pd.DataFrame, pd.DataFrame, pd.DataFrame]:

        if countIndex % 100 == 0:
            logger.info(f"MainWrapperKR - createDataframe : {countIndex}")

        globalDataframeMain = CF.generateEmptyDataframe("Main")
        globalDataframePredictions = CF.generateEmptyDataframe("Prediction")
        globalDataframeWindow = CF.generateEmptyDataframe("Window")

        startDate = CF.getNextPredictionDate(
            callDate - datetime.timedelta(CONF.TOTAL_REQUEST_DATE_LENGTH)
        )
        endDate = callDate

        try:
            tmpQuery = all_Stockitems.filter(
                Q(stock_name__stock_tick__stock_tick=tick)
              & Q(reg_date__range=(startDate, endDate)) # get only needed dates
            ).order_by('-reg_date')

            if not tmpQuery.exists():
                raise Exception(f"Empty Database for tick : {tick}")

            previousAnswer = None
            for idx, stockitem in enumerate(tmpQuery):
                tmp_regDate = stockitem.reg_date
                tmp_regDatetime = datetime.datetime(tmp_regDate.year, tmp_regDate.month, tmp_regDate.day)
                tmpInsertData = {
                    'section_integer' : int(stockitem.stock_map_section.section_name.section_integer),
                    'total_sum' : int(stockitem.stock_map_section.total_sum),
                    'time_elapsed' : abs(int((callDate - tmp_regDatetime).days)),
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
                # elif idx == 1 and False: # remove data lookahed
                #     tmpInsertData["answer"] = previousAnswer
                #     globalDataframeWindow = globalDataframeWindow.append(
                #         tmpInsertData, ignore_index=True
                #     )
                #     previousAnswer = stockitem.close
                else:
                    tmpInsertData["answer"] = previousAnswer
                    globalDataframeMain = globalDataframeMain.append(
                        tmpInsertData, ignore_index=True
                    )
                    previousAnswer = stockitem.close

        except Exception as e:
            logger.warning(f"appStockPrediction - MainWrapperKR - createDataframe; {e}")

        finally:
            return globalDataframeMain, globalDataframePredictions, globalDataframeWindow

def myMPE( y_pred, y_true):
    return np.mean((y_true - y_pred) / y_true) * 100

# active information columns only selected
# exist_stockitems = StockItem.objects.filter(
#     stock_map_section__stock_tick__stock_isInfoAvailable=True
# ).values_list(flat=True)