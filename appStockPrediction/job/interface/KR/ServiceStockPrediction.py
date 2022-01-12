import traceback
import StockManager.subSettings as CONFI

from django.db.models import Count
from django.db.models.query import QuerySet, Q, F
from bulk_update.helper import bulk_update
from appStockInfo.models import (
    StockItem,
    StockTick,
    StockItemListName
)
from appStockPrediction.models import (
    StockPredictionHistory
)
from appStockPrediction.job.interface.predictionModels.builder import Builder

import ConfigFile as CONF
import CommonFunction as CF

from sklearn.model_selection import train_test_split
"""
score in sklearn : https://scikit-learn.org/stable/modules/classes.html#sklearn-metrics-metrics

"""

import datetime
import pandas as pd

import logging
logger = logging.getLogger('appStockPrediction')


class MainWrapperKR:


    def __init__(self):pass

    def doAction(self, isCallCurrentDatetime:bool=True):
        logger.info("MainWrapperKR - doAction")

        if isCallCurrentDatetime:
            self.deleteStockPredictionHistory(datetime.datetime.now())
            self.createStockPredictionHistory(datetime.datetime.now())
        else:
            self.deleteStockPredictionHistory(datetime.datetime(2022,1,7,10))
            self.createStockPredictionHistory(datetime.datetime(2022,1,7,10))


    def deleteStockPredictionHistory(self, callDate:datetime.datetime):
        logger.info("MainWrapperKR - deleteStockPredictionHistory")

        # 모든것을 지움 -> 일자 지난 것에 대해서
        time_End = CF.getNextPredictionDate(callDate)
        time_Start = CF.getNextPredictionDate(
            time_End - datetime.timedelta(days=CONF.MAX_DAYS_KEEP_OLD_STOCKITEMS)
        )

        tmpQuery = StockPredictionHistory.objects.filter(~Q(prediction_time__gte=time_Start))
        logger.info(f"MainWrapperKR - deleteStockPredictionHistory; Total deleted number of history : {len(tmpQuery)}")
        logger.info(f"MainWrapperKR - deleteStockPredictionHistory; Start : {time_Start}, End : {time_End}")
        tmpQuery.delete()


    def createStockPredictionHistory(self, callDate:datetime.datetime):
        """
        StockPrediction CRUD
        """
        logger.info("MainWrapperKR - createStockPredictionHistory")

        predictionDF, predictionDay = self.createPrediction(callDate=callDate)
        # print(f'predictionDF.head(3) : {predictionDF.head(3)}')


        logger.info(f"MainWrapperKR - createStockPredictionHistory; predictionDay : {predictionDay}, callDate : {callDate}")
        filter_1 = []
        filter_2 = []

        # Delete unmade prediction stockticks
        # predictionStockTicksList = predictionDF["tick"].tolist()
        # tmpQueryDelete = StockPredictionHistory.objects.filter(
        #     ~Q(stock_tick__stock_tick__in=predictionStockTicksList)
        # )
        # logger.info(f"MainWrapperKR - createStockPredictionHistory; deleted unwanted prediction history")
        # logger.info(f"MainWrapperKR - createStockPredictionHistory; deleted unwanted datas length : {len(tmpQueryDelete)}")
        # tmpQueryDelete.delete()


        tmpPredictionDayFilter = StockPredictionHistory.objects.all()
        for idx, row in predictionDF.iterrows():
            try:
                tmpTick = row['tick']
                tmpPrediction = row['prediction']
                tmpClose = row['close']
                tmpOpen = row['open']
                tmpGap = row['gap']

                # for CRUD
                # Not existing
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
                            #prediction=((tmpPrediction - tmpClose) / tmpClose) * 100,
                            prediction=( tmpPrediction / tmpClose ) * 100,
                            value=tmpPrediction,
                            initial_close=tmpClose
                        )
                    )
                else: # existing
                    tmp_StockPredictionHistory = tmpPredictionDayFilter.get(
                        stock_tick__stock_tick=tmpTick,
                        prediction_time=predictionDay
                    )
                    # update
                    filter_2.append(tmpTick)
                    tmp_StockPredictionHistory.prediction = (tmpPrediction / tmpClose ) *100 # ((tmpPrediction + tmpOpen - tmpClose) / tmpClose)*100
                    tmp_StockPredictionHistory.value = tmpPrediction
                    tmp_StockPredictionHistory.initial_close = tmpClose

            except Exception as e:
                logger.info(f"MainWrapperKR - createStockPredictionHistory; Error happened : {e}")
                #traceback.print_exc()

        # Bulk update
        bulk_update(tmpPredictionDayFilter)

        # Bulk create
        StockPredictionHistory.objects.bulk_create(
            filter_1
        )



        logger.info(f"MainWrapperKR - createStockPredictionHistory; Total new objects : {len(filter_1)}")
        logger.info(f"MainWrapperKR - createStockPredictionHistory; Total updated objects : {len(filter_2)}")


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
        tmpMainDF['market_name']    = pd.to_numeric(tmpMainDF['market_name'], errors='coerce')

        tmpPredDF['section_integer'] = pd.to_numeric(tmpPredDF['section_integer'], errors='coerce')
        tmpPredDF['total_sum']       = pd.to_numeric(tmpPredDF['total_sum'], errors='coerce')
        tmpPredDF['time_elapsed']    = pd.to_numeric(tmpPredDF['time_elapsed'], errors='coerce')
        tmpPredDF['market_name']    = pd.to_numeric(tmpPredDF['market_name'], errors='coerce')

        # Gen data
        if not CONFI.IS_MAIN_SERVER:
            if CONFI.DEBUG:
                print(f'tmpMainDF')
                print(f'len(tmpMainDF) : {len(tmpMainDF)}')
                tmpMainDF.info()
                tmpMainDF.head(3)
                print(f'tmpPredDF')
                print(f'len(tmpPredDF) : {len(tmpPredDF)}')
                tmpPredDF.info()
                tmpPredDF.head(3)
                #
                import pickle, os
                from pathlib import Path
                root = Path(__file__).resolve().parent.parent.parent.parent
                print(f'root : {root}')
                with open(
                        os.path.join(
                            root,
                            'testMockData', 'tmpMainDF.p'
                        ), 'wb') as f:
                    pickle.dump(tmpMainDF, f)
                    print(f'successful 1')


                with open(
                        os.path.join(
                            root,
                            'testMockData', 'tmpPredDF.p'
                        ), 'wb') as f:
                    pickle.dump(tmpPredDF, f)
                    print(f'successful 2')


        # from Main Dataframe
        X, Y = tmpMainDF.loc[:, :'roe'], tmpMainDF.loc[:, 'answer':'answer']

        # from Prediction Dataframe -> "answer" column is not present here
        PX, PX_indexTick = tmpPredDF.loc[:, :'roe'], tmpPredDF.loc[:, 'tick':]

        """
        Param explained : https://towardsdatascience.com/a-guide-to-xgboost-hyperparameters-87980c7f44a9
        Hyper and more : https://xgboost.readthedocs.io/en/latest/parameter.html
        """
        X_train, X_test, y_train, y_test =  train_test_split(X, Y, test_size=0.2)

        # Build and predict
        real_predictions = Builder.build(model_type="XGBoost",
                                         X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test,
                                         PX=PX
                                         )

        PX_indexTick['prediction'] = real_predictions.tolist()
        PX_indexTick['close'] = PX['close']
        PX_indexTick['open'] = PX['open']
        PX_indexTick['gap'] = PX['gap']

        #print(f'PX_indexTick.head(3) : {PX_indexTick.head(3)}')

        # get Date
        try:
            latestDate = callDate
            # tmplatest = StockItem.objects.filter(
            #     Q(stock_name__stock_tick__stock_isInfoAvailable=True)
            # ).order_by('-reg_date').first()
            #
            # tmplatestDate = tmplatest.reg_date
            #
            # latestDate = datetime.datetime(tmplatestDate.year,
            #                                tmplatestDate.month,
            #                                tmplatestDate.day, hour=CONF.MARKET_TOTAL_FINISH_HOUR)
        except: latestDate = datetime.datetime.now()

        # Convert to Numeric
        PX_indexTick['prediction'] = pd.to_numeric(PX_indexTick['prediction'], errors='coerce')
        PX_indexTick['close']       = pd.to_numeric(PX_indexTick['close'], errors='coerce')
        PX_indexTick['open']    = pd.to_numeric(PX_indexTick['open'], errors='coerce')
        PX_indexTick['gap']    = pd.to_numeric(PX_indexTick['gap'], errors='coerce')

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

        globalDataframeMain = CF.generateEmptyDataframe("Main")
        globalDataframePredictions = CF.generateEmptyDataframe("Prediction")
        globalDataframeWindow = CF.generateEmptyDataframe("Window")

        # startDate = CF.getNextPredictionDate(
        #     callDate - datetime.timedelta(CONF.TOTAL_REQUEST_DATE_LENGTH)
        # )
        startDate = CF.getStartFetchingDate(callStartDate=callDate)
        endDate = CF.getEndFetchingDate(callEndDate=callDate)

        if countIndex % 100 == 0:
            logger.info(f"MainWrapperKR - createDataframe : {countIndex}")
            logger.info(f"MainWrapperKR - createDataframe; start:{startDate}, end:{endDate}")

        try:
            tmpStockTicksByVolumeFilter = (all_Stockitems.order_by('-volume')
                                 .values_list('stock_name__stock_tick__stock_tick', flat=True)
                                 .distinct()
                               ) # 한번이라도 상위에 들은 거래량인 경우 -> CONF.TOP_VOULME_FILTER
            tmpQuery = all_Stockitems.filter(
                Q(stock_name__stock_tick__stock_tick__in=tmpStockTicksByVolumeFilter[:int(
                                                            len(tmpStockTicksByVolumeFilter)*CONF.TOP_VOULME_FILTER
                )])
              & Q(stock_name__stock_tick__stock_tick=tick)
              & Q(reg_date__range=(startDate, endDate)) # get only needed dates
              & (
                    ~(    # Remove unwanted (거래 중지)
                          Q(open=0)
                        | Q(high=0)
                        | Q(low=0)
                        | Q(close=0)
                      )
                 )
              & (
                    Q(close__gte=CONF.KR_BOTTOMLINE) # applies only for first object
                )
            ).order_by('-reg_date')

            if not tmpQuery.exists():
                raise Exception(f"DB Empty for tick : {tick}")

            if countIndex % 100 == 0:
                logger.info(f"MainWrapperKR - createDataframe; Query return length check : {len(tmpQuery)}")

            previousAnswer = None
            for idx, stockitem in enumerate(tmpQuery):
                tmp_regDate = stockitem.reg_date
                tmp_regDatetime = datetime.datetime(tmp_regDate.year, tmp_regDate.month, tmp_regDate.day)
                tmpInsertData = {
                    'section_integer' : int(stockitem.stock_map_section.section_name.section_integer),
                    'total_sum' : int(stockitem.stock_map_section.total_sum / CONF.STOCK_NUM_NORMALIZER),
                    'time_elapsed' : abs(int((callDate - tmp_regDatetime).days)),
                    'open' : stockitem.open,
                    'high' : stockitem.high,
                    'low' : stockitem.low,
                    'close' : stockitem.close,
                    'gap' : stockitem.close - stockitem.open,
                    'volume' : stockitem.volume,
                    'div' : stockitem.div,
                    'per' : stockitem.per,
                    'pbr' : stockitem.pbr,
                    'market_name': CF.getMarketNumber(stockitem.stock_name.stock_tick.stock_marketName),
                    'roe' : stockitem.roe,
                    'tick' : str(tick)
                }
                if idx == 0:  # first index which needs predictions
                    globalDataframePredictions = globalDataframePredictions.append(
                        tmpInsertData, ignore_index=True
                    )
                    previousAnswer = stockitem.close - stockitem.open
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
                    previousAnswer = stockitem.close - stockitem.open

        except Exception as e:
            logger.warning(f"appStockPrediction - MainWrapperKR - createDataframe; {e}")

        finally:
            return globalDataframeMain, globalDataframePredictions, globalDataframeWindow

