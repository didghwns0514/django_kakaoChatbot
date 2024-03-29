import traceback
import os

import StockManager.subSettings as CONFI

from django.db.models import Q, F
from bulk_update.helper import bulk_update
from appStockInfo.models import (
    StockTick,
    StockItemListName,
    StockItem,
    StockSection,
    StockLastUpdateTime,
    StockItemListSection
)
import ConfigFile as CONF
import CommonFunction as CF

from pykrx import stock
# import yfinance

from datetime import datetime, timedelta
import pandas as pd
import requests as rq
from io import BytesIO
import time



import logging
logger = logging.getLogger('appStockInfo')


class MainWrapperKR:

    def __init__(self):

        self.stockList = GetStockList()
        self.stockInfo = GetStockInfo()


    def doAction(self, isDataFetchOn:bool=True):
        logger.info("MainWrapperKR - doAction")
        IS_DATA_FETCH_NEEDED = True
        CF.clearConnections()
        #self.getLoggerForAllInfos()

        if isDataFetchOn:
            if CONFI.DEBUG:
                IS_DATA_FETCH_NEEDED = bool(int(os.environ.get('IS_DATA_FETCH_NEEDED')))

        if IS_DATA_FETCH_NEEDED:
            self.stockList.doAction()
            self.stockInfo.doAction(self.stockList.KOSPI, self.stockList.KOSDAQ, GetStockList.INDEX_KRPYX)

            # CRUD
            # 1) Create StockTick
            CF.clearConnections()
            self.createStockTick(self.stockList.KOSPI, "KOSPI")
            CF.clearConnections()
            self.createStockTick(self.stockList.KOSDAQ, "KOSDAQ")
            CF.clearConnections()
            self.createStockTick(GetStockList.INDEX_KRPYX, "KOSPI")

            # 2) Create StockItemListName
            CF.clearConnections()
            self.createStockItemListName(self.stockList.KOSPI, "KOSPI")
            CF.clearConnections()
            self.createStockItemListName(self.stockList.KOSDAQ, "KOSDAQ")
            CF.clearConnections()
            self.createStockItemListName(GetStockList.INDEX_KRPYX, "KOSPI")


            # 3) Create StockSection
            CF.clearConnections()
            self.createStockSection()
            CF.clearConnections()
            self.createStockItemListSection()

            # 4-1) Delete StockItems
            CF.clearConnections()
            self.deleteStockItem(datetime.now())
            # 4-2) Create StockItems
            CF.clearConnections()
            self.createStockItem(datetime.now())

        # 5) Create DateStamp
        CF.clearConnections()
        self.updateStockLastUpdateTime(dateStamp=datetime.now())



    def createStockTick(self, listStocks: list, marketName: str = 'Dummy'):
        """
        create ticker CRUD
        > if info is not provided, set to False; from StockItem object
        > if Ticker doesn't exist, add

        [ORM]
        stock_tick : Stock 코드
        stock_marketName : 등록된 마켓 이름
        stock_isInfoAvailable : Fetch된 market 데이터 존재하는 경우
            -> StockItem 등록시, 데이터 없으면 False로 다시 세팅
        """
        logger.info("MainWrapperKR - createStockTick")

        # update isInfoAvailable
        # all_stocktick = StockTick.objects.all()
        # if all_stocktick.exists():
        #     for stock_tick in all_stocktick:
        #         stock_tick.stock_isInfoAvailable = True
        #
        #     # bulk update
        #     bulk_update(all_stocktick)

        # get all stock ticks
        exsist_stocktick = StockTick.objects.all().values_list('stock_tick', flat=True)

        update_exist_stocktick = set(exsist_stocktick) & set(listStocks)
        create_new_stocktick = set(listStocks) - set(exsist_stocktick)

        # create new stock
        filter_2 = []
        for stock_tick in create_new_stocktick:
            filter_2.append(
                StockTick(
                    stock_tick=stock_tick,
                    stock_marketName=marketName,
                    stock_isInfoAvailable=True
                )
            )

        StockTick.objects.bulk_create(filter_2)


    def createStockItemListName(self, listStocks: list, marketName: str = 'Dummy'):
        """
        create ticker to name CRUD
        > if Ticker exists, and Name isNot provided, it will be replaced with a ticker

        [ORM]
        stock_tick : ForeignKey - Stock 코드
        stock_name : 실제 종목 이름 Mapping 값
        """
        logger.info("MainWrapperKR - createStockItemListName")

        query_set = StockItemListName.objects.all()
        exsist_stocktick = query_set.values_list('stock_tick__stock_tick', flat=True)
        exist_needsupdate_stocktick = StockItemListName.objects.filter(stock_name__regex="(\D|\w)*") # "^[a-zA-Z0-9]*$"  # "^[a-zA-Z0-9 \(\)]*$"
        create_new_stocktick = set(listStocks) - set(exsist_stocktick)

        # create new stock list item, update record
        filter_1 = []
        filter_2 = []
        for stock_tick in create_new_stocktick:
            # ticker - 회사 이름 업데이트
            if stock_tick not in self.stockList.tickerToName:
                tmpNameData = str(stock_tick)
            else:
                tmpNameData = self.stockList.tickerToName[stock_tick]

            try:
                tmpStockTick = StockTick.objects.filter(stock_tick=stock_tick)
                if tmpStockTick.exists():  # 존재한다면
                    filter_2.append(
                        StockItemListName(
                            stock_tick=tmpStockTick.first(),
                            stock_name=tmpNameData
                        )
                    )
                else:  # 존재하지 않는다면, create 이후 업데이트
                    tmpCreateStockTick = StockTick(
                        stock_tick=stock_tick,
                        stock_marketName=marketName,
                        stock_isInfoAvailable=True
                    )
                    filter_1.append(tmpCreateStockTick)
                    filter_2.append(
                        StockItemListName(
                            stock_tick=tmpCreateStockTick,
                            stock_name=tmpNameData
                        )
                    )
            except:
                pass

        logger.info(f"MainWrapperKR - createStockItemListName; exist_needsupdate_stocktick length : {len(exist_needsupdate_stocktick)}")
        if exist_needsupdate_stocktick.exists():
            #print(f'len of exists of needsupdate : {len(exist_needsupdate_stocktick)}')
            for stock_item in exist_needsupdate_stocktick:
                if str(stock_item.stock_tick.stock_tick) not in self.stockList.tickerToName:
                    continue
                else:
                    stock_item.stock_name = self.stockList.tickerToName[str(stock_item.stock_tick.stock_tick)]
            # update
            bulk_update(exist_needsupdate_stocktick)

        # create
        StockTick.objects.bulk_create(filter_1)
        StockItemListName.objects.bulk_create(filter_2)
        logger.info(f"MainWrapperKR - createStockItemListName; new stock name created length : {len(filter_2)}")


    def createStockSection(self):
        """
        Stock Sections mapping
        > Non existing will be added

        [ORM]
        if Relational Field doesn't exist in the table, return others
        -> create "Others"
        """
        logger.info("MainWrapperKR - createStockSection")

        tmpOthers = StockSection.objects.filter(section_name="Others")
        if not tmpOthers.exists():
            StockSection.objects.create(
                section_name="Others"
            )

        tmpStockSectionDF = self.stockInfo.infoFinanceData
        if isinstance(tmpStockSectionDF, pd.DataFrame) and '업종명' in tmpStockSectionDF:  # is a dataframe
            tmpStockSectionCol = tmpStockSectionDF['업종명'].tolist()
            tmpStockSectionDB = StockSection.objects.all().values_list('section_name', flat=True)
            create_new_stocksection = set(tmpStockSectionCol) - set(tmpStockSectionDB)

            filter_1 = []

            for section in create_new_stocksection:
                filter_1.append(
                    StockSection(
                        section_name=section
                    )
                )
            StockSection.objects.bulk_create(filter_1)

        else:  # not a dataframe
            logger.warning("MainWrapperKR - createStockSection; infoFinanceData Not a dataframe")


    def createStockItemListSection(self):
        """
        Stock Sections individual stock to section mapping
        > Non existing will be added

        [ORM]
        if Relational Field doesn't exist in the table, return others
        -> create "Others"
        """
        logger.info("MainWrapperKR - createStockItemListSection")

        tmpStockSectionDF = self.stockInfo.infoFinanceData


        if isinstance(tmpStockSectionDF, pd.DataFrame) and '업종명' in tmpStockSectionDF:  # is a dataframe
            filter_1 = []
            cnt_exist = 0
            tmpStockTickCol = tmpStockSectionDF['종목코드'].tolist()

            # 없는 종목 (추가해야하는지 확인)
            query_stocklistSection = StockItemListSection.objects.all()
            tmp_exist_stockList = query_stocklistSection.values_list('stock_tick__stock_tick', flat=True)

            tmp_new_stockticks = StockTick.objects.all().values_list('stock_tick', flat=True)
            tmp_new_stocksets = set(set(tmp_new_stockticks) - set(tmp_exist_stockList))
            if tmp_new_stocksets:
                logger.critical("MainWrapperKR - createStockItemListSection; Update CSV")
                logger.critical(
                    f"MainWrapperKR - createStockItemListSection; Missing information/new stockticks  : \n{tmp_new_stocksets}")

            create_new_stocklistsection = \
                set(tmpStockTickCol) - set(tmp_exist_stockList)
            logger.critical(
                f"MainWrapperKR - createStockItemListSection; Missing information/new stocklistsection  : \n{create_new_stocklistsection}")

            for tick in create_new_stocklistsection:
                try:
                    # 없으면 create
                    if not query_stocklistSection.filter(Q(stock_tick__stock_tick=tick)).exists():
                        # StockTick 구하기
                        tmpStockTick = StockTick.objects.get(
                            stock_tick=tick
                        )

                        # Section 구하기
                        try:  # 없으면 Other 할당
                            # section = str(selectedDF["업종명"])
                            section = str(
                                tmpStockSectionDF.loc[tmpStockSectionDF['종목코드'] == tick, '업종명'].values[0]
                            )
                        except:
                            section = str("Other")
                        tmpSectionName = StockSection.objects.get(
                            section_name=section
                        )

                        # totalSum 구하기
                        tmpTotalSum = int(
                            tmpStockSectionDF.loc[tmpStockSectionDF['종목코드'] == tick, "시가총액"].values[0]
                        )

                        filter_1.append(
                            StockItemListSection(
                                stock_tick=tmpStockTick,
                                section_name=tmpSectionName,
                                total_sum=tmpTotalSum
                            )
                        )
                    else: cnt_exist += 1
                except:
                    continue

            StockItemListSection.objects.bulk_create(filter_1)
            logger.info(f"MainWrapperKR - createStockItemListSection; cnt_exist : {cnt_exist}")
        else:
            logger.warning("MainWrapperKR - createStockItemListSection; infoFinanceData Not a dataframe")



    def deleteStockItem(self, dateStamp:datetime):
        logger.info("MainWrapperKR - deleteStockItem")

        # 모든것을 지움 -> 일자 지난 것에 대해서
        time_End = dateStamp
        time_Start = CF.getNextPredictionDate(
            time_End - timedelta(days=CONF.MAX_DAYS_KEEP_OLD_STOCKITEMS)
        )

        StockItem.objects.filter(~Q(reg_date__range=(time_Start, time_End))).delete()


    def createStockItem(self, callDate:datetime):
        """
        create StockItem CRUD
        """
        # exsist_stocktick = StockItemListName.objects.filter(stock_tick__stock_isInfoAvailable=True)
        logger.info("MainWrapperKR - createStockItem")

        # 정보 lookup 세팅
        filter_1 = []
        filter_2 = []

        # Data 축적
        # pull from Info
        tmpInfoBasicKOSPI = self.stockInfo.infoBasicKOSPI
        tmpTickerBasicKOSPI = self.stockInfo.infoTickerKOSPI
        tmpInfoBasicKOSDAQ = self.stockInfo.infoBasicKOSDAQ
        tmpTickerBasicKOSDAQ = self.stockInfo.infoTickerKOSDAQ

        globalInfoBasic = {**tmpInfoBasicKOSPI, **tmpInfoBasicKOSDAQ}
        globalTickerBasic = {**tmpTickerBasicKOSPI, **tmpTickerBasicKOSDAQ}

        # total iteration
        #exist_stockticks = StockTick.objects.all().values_list('stock_tick', flat=True)
        # query_stockticks = StockTick.objects.filter(stock_isInfoAvailable=True)
        # query_stockitems = StockItem.objects.filter(stock_name__stock_tick__stock_isInfoAvailable=True)
        query_stockticks = StockTick.objects.all()
        query_stockitems = StockItem.objects.all()
        exist_stockticks = query_stockticks.values_list('stock_tick', flat=True)

        for tick in exist_stockticks: # 새로운 stock tick 포함 모든 stock tick
            try:
                if tick in globalInfoBasic and tick in globalTickerBasic:
                    selectedInfoBasic = globalInfoBasic[tick]
                    selectedTickerBasic = globalTickerBasic[tick]

                    # Dataframe prep
                    concatDF = pd.concat(
                        [
                            selectedInfoBasic,
                            selectedTickerBasic
                        ], axis=1
                    )

                    # New column
                    concatDF['ROE'] = concatDF['EPS'] / concatDF['BPS'] * 100

                    # -> Nan value removal
                    # https://rfriend.tistory.com/542
                    # https://rfriend.tistory.com/262
                    fill_missing_nan = {
                        'ROE': 0,
                        '거래량': 0,
                        '시가': concatDF['종가'].bfill(),
                        '고가': concatDF['종가'].bfill(),
                        '저가': concatDF['종가'].bfill(),
                        '종가': concatDF['종가'].bfill(),

                        'BPS': concatDF['BPS'].bfill(),
                        'PER': concatDF['PER'].bfill(),
                        'PBR': concatDF['PBR'].bfill(),
                        'EPS': concatDF['EPS'].bfill(),
                        'DIV': concatDF['DIV'].bfill()
                    }
                    concatDF.fillna(fill_missing_nan, inplace=True)  # removal inplace

                    # if missing Nan still exists
                    if concatDF.isnull().values.any() :
                        filter_2.append(tick)
                        continue


                    # Foreign Key
                    tmpStockListSection = StockItemListSection.objects.get(
                        stock_tick=tick
                    )
                    tmpStockName = StockItemListName.objects.get(
                        stock_tick=tick
                    )

                    # Check for existing records that doesn't need update
                    # filter tick's date onece more
                    stockItemsQuery = query_stockitems.filter(
                             Q(stock_name__stock_tick__stock_tick=tick)
                        ).order_by('-reg_date')

                    if stockItemsQuery.exists():

                        latestDate = stockItemsQuery.first().reg_date
                        oldestDate = stockItemsQuery.last().reg_date

                        # Pick between range
                        concatDF = concatDF[
                            (concatDF.index < str(oldestDate)) | (concatDF.index > str(latestDate))
                        ]


                    # iteration
                    for idx, row in concatDF.iterrows():
                        reg_date = idx
                        open = row["시가"]
                        high = row["고가"]
                        low = row["저가"]
                        close = row["종가"]
                        volume = row["거래량"]
                        div = row["DIV"]
                        per = row["PER"]
                        pbr = row["PBR"]
                        roe = row["ROE"]
                        filter_1.append(
                            StockItem(
                                stock_name=tmpStockName,
                                stock_map_section=tmpStockListSection,
                                reg_date=reg_date,
                                open=open,
                                high=high,
                                low=low,
                                close=close,
                                volume=volume,
                                div=div,
                                per=per,
                                pbr=pbr,
                                roe=roe
                            )
                        )

                else:
                    """
                    if no dataframe is retrieved
                    -> Check if data exists
                    """
                    startDate = CF.getStartFetchingDate(callStartDate=callDate)
                    endDate = callDate
                    stockItemsQuery = query_stockitems.filter(
                             Q(stock_name__stock_tick__stock_tick=tick)
                          &  Q(reg_date__range=(startDate, endDate))
                        ).order_by('-reg_date')

                    if stockItemsQuery.exists() and stockItemsQuery.count() >= CONF.PREDICTION_WINDOW_LENGTH:
                        # wanted data length already exists
                        pass # skip
                    else:
                        logger.critical(f"MainWrapperKR - StockItem no DF and not enought data : {tick}")
                        filter_2.append(tick)

            except Exception as e:
                logger.critical(f"MainWrapperKR - StockItem error : {e}")
                #traceback.print_exc()
                filter_2.append(tick)

        # update Non information available Object
        logger.info(f"MainWrapperKR - total info not available : {len(filter_2)}")

        # create
        StockItem.objects.bulk_create(filter_1)

        # update not available information
        tmpQuerySet = StockTick.objects.filter(stock_tick__in=filter_2)
        if tmpQuerySet.exists():
            for stock_tick in tmpQuerySet:
                stock_tick.stock_isInfoAvailable = False
            # StockTick.objects.bulk_update(tmpQuerySet,
            #                               fields=['stock_isInfoAvailable'])
            bulk_update(tmpQuerySet)


    def updateStockLastUpdateTime(self, dateStamp):
        """
        update dateime of last update of KR stocks
        """
        logger.info("appStockInfo - MainWrapperKR - updateStockLastUpdateTime")

        StockLastUpdateTime.objects.create(
            update_time=dateStamp
        )


    def getLoggerForAllInfos(self):
        """
        to log informations given
        """
        # Dictionary
        tmpInfoTickerKOSPI = self.stockInfo.infoTickerKOSPI
        tmpInfoTickerKOSDAQ = self.stockInfo.infoTickerKOSDAQ
        tmpInfoBasicKOSPI = self.stockInfo.infoBasicKOSPI
        tmpInfoBasicKOSDAQ = self.stockInfo.infoBasicKOSDAQ

        # List
        tmpTickerKOSPI = self.stockList.KOSPI
        tmpTickerKOSDAQ = self.stockList.KOSDAQ

        # Check overlap
        tmpOverlapp = set(tmpTickerKOSPI) & set(tmpTickerKOSDAQ)

        logger.info(f"getLoggerForAllInfos - tmpInfoTickerKOSPI : {set(tmpInfoTickerKOSPI.keys())}")
        logger.info(f"getLoggerForAllInfos - tmpInfoTickerKOSDAQ : {set(tmpInfoTickerKOSDAQ.keys())}")
        logger.info(f"getLoggerForAllInfos - tmpInfoBasicKOSPI : {set(tmpInfoBasicKOSPI.keys())}")
        logger.info(f"getLoggerForAllInfos - tmpInfoBasicKOSDAQ : {set(tmpInfoBasicKOSDAQ.keys())}")
        logger.info(f"getLoggerForAllInfos - tmpTickerKOSPI : {set(tmpTickerKOSPI)}")
        logger.info(f"getLoggerForAllInfos - tmpTickerKOSDAQ : {set(tmpTickerKOSDAQ)}")
        logger.info(f"getLoggerForAllInfos - tmpOverlapp : {tmpOverlapp}")

class GetStockList:

    INDEX_CODE_KOSPI = [
        "069500",  # KODEX 200
        "252670",  # KODEX 200선물인버스2X
        "122630",  # KODEX 레버리지
        "233740",  # KODEX 코스닥150 레버리지
        "114800",  # KODEX 인버스

    ]
    INDEX_KRPYX = [
        "1001", # 코스피
        "1028", # 코스피 200
    ]

    def __init__(self):
        self.KOSDAQ = []
        self.KOSPI = []
        self.ALL = []
        self.tickerToName = {}

    def doAction(self):
        logger.info("GetStockList - doAction")
        self.getMarketTickers()
        self.getTickerNameKOSDAQ()
        self.getTickerNameKOSPI()
        self.getTickerNameINDEX()


    def getMarketTickers(self):
        logger.info("GetStockList - getMarketTickers")

        for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
            try:
                tmpData1 = list(set(stock.get_market_ticker_list(market="KOSDAQ")))
                if tmpData1:
                    self.KOSDAQ = tmpData1
                    logger.info(f"GetStockList - getMarketTickers; KOSDAQ Total data retrieved : {len(self.KOSDAQ)}")
                    break
            except: pass
            time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)

        else:
            logger.critical("GetStockList - getMarketTickers; KOSDAQ No data retrieved")


        for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
            try:
                tmpData2 = list(set(stock.get_market_ticker_list(market="KOSPI")))
                if tmpData2:
                    self.KOSPI = tmpData2
                    # self.KOSPI += GetStockList.INDEX_CODE_KOSPI
                    logger.info(f"GetStockList - getMarketTickers; KOSPI Total data retrieved : {len(self.KOSPI)}")
                    break
            except:pass
            time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)

        else:
            logger.critical("GetStockList - getMarketTickers; KOSPI No data retrieved")


        for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
            try:
                tmpData3 = list(set(stock.get_market_ticker_list(market="ALL")))
                if tmpData3:
                    self.ALL = tmpData3
                    logger.info(f"GetStockList - getMarketTickers; ALL Total data retrieved : {len(self.ALL)}")
                    break
            except:pass
            time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)

        else:
            logger.critical("GetStockList - getMarketTickers; ALL No data retrieved")

    def getTickerNameKOSDAQ(self):
        logger.info("GetStockList - getTickerNameKOSDAQ")
        for stockTicker in self.KOSDAQ:
            try:
                self.tickerToName[stockTicker] = stock.get_market_ticker_name(stockTicker)
            except:
                self.tickerToName[stockTicker] = stockTicker
                logger.critical(f"GetStockList - getTickerNameKOSDAQ; No name retrieved, ticker : {stockTicker}")


    def getTickerNameKOSPI(self):
        logger.info("GetStockList - getTickerNameKOSPI")
        for stockTicker in self.KOSPI:
            try:
                self.tickerToName[stockTicker] = stock.get_market_ticker_name(stockTicker)
            except:
                self.tickerToName[stockTicker] = stockTicker
                logger.critical(f"GetStockList - getTickerNameKOSPI; No name retrieved, ticker : {stockTicker}")

    def getTickerNameALL(self):
        logger.info("GetStockList - getTickerNameALL")
        for stockTicker in self.ALL:
            try:
                self.tickerToName[stockTicker] = stock.get_market_ticker_name(stockTicker)
            except:
                self.tickerToName[stockTicker] = stockTicker
                logger.critical(f"GetStockList - getTickerNameALL; No name retrieved, ticker : {stockTicker}")

    def getTickerNameINDEX(self):
        logger.info("GetStockList - getTickerNameINDEX")
        for stockTicker in GetStockList.INDEX_KRPYX:
            try:
                self.tickerToName[stockTicker] = stock.get_index_ticker_name(stockTicker)
            except:
                self.tickerToName[stockTicker] = stockTicker
                logger.critical(f"GetStockList - getTickerNameINDEX; No name retrieved, ticker : {stockTicker}")

    def __str__(self) -> str:
        return f'KOSDAQ : \n {self.KOSDAQ[:10]}  \nKOSPI : \n {self.KOSPI[:10]}\nKONEX : \n {self.ALL[:10]}'


class GetStockInfo:
    TOTAL_REQUEST_DATE_LENGTH = CONF.TOTAL_REQUEST_DATE_LENGTH

    def __init__(self):
        self.infoBasicKOSDAQ = {}
        self.infoBasicKOSPI = {}
        self.infoTickerKOSDAQ = {}
        self.infoTickerKOSPI = {}
        self.infoBasicINDEX = {}
        self.infoTickerINDEX = {}

        self.infoFinanceData = None


    def doAction(self, listKOSPI: list, listKOSDAQ: list, listINDEX: list):
        logger.info("GetStockInfo - doAction")
        self.getBasicKOSPI(listKOSPI)
        self.getTickerKOSPI(listKOSPI)

        self.getBasicKOSDAQ(listKOSDAQ)
        self.getTickerKOSDAQ(listKOSDAQ)

        self.getBasicINDEX(listINDEX)
        self.getTickerINDEX(listINDEX)

        self.getFinanceData()


    def getFinanceData(self):
        """업종 데이터"""
        logger.info("GetStockInfo - getFinanceData")

        for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
            self.infoFinanceData = FinaceInformation("KRX")
            if not ((not self.infoFinanceData.empty) and '업종명' in self.infoFinanceData):
                time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)
                continue
            else:  # got right data
                logger.info(f"GetStockInfo - getFinanceData; Finance Total data length : {len(self.infoFinanceData)}")
                break

        else:
            logger.critical("GetStockInfo - getFinanceData; Empty Dataframe")


    def getBasicKOSDAQ(self, listKOSDAQ: list):
        logger.info("GetStockInfo - getBasicKOSDAQ")
        for stockID in listKOSDAQ:

            for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
                try:
                    startDay = self.setTimeFormat(CF.getStartFetchingDate(datetime.now()), haveSeparator=False)
                    endDay = self.setTimeFormat(datetime.today(), haveSeparator=False)
                    logger.info(f"GetStockInfo - getBasicKOSDAQ; startDay : {startDay}, endDay : {endDay}")
                    tmpData = stock.get_market_ohlcv_by_date(
                        fromdate=startDay,
                        todate=endDay,
                        ticker=stockID,
                        name_display=False
                    )

                    if not tmpData.empty:
                        self.infoBasicKOSDAQ[stockID] = tmpData
                        break

                except:pass
                time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)
            else:
                logger.critical(f"GetStockInfo - getBasicKOSDAQ; Empty Dataframe, ticker : {stockID}")
        logger.info(f"GetStockInfo - getBasicKOSDAQ; getBasic Total data length : {len(self.infoBasicKOSDAQ)}")


    def getTickerKOSDAQ(self, listKOSDAQ: list):
        logger.info("GetStockInfo - getTickerKOSDAQ")
        for stockID in listKOSDAQ:

            for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
                try:
                    startDay = self.setTimeFormat(CF.getStartFetchingDate(datetime.now()), haveSeparator=False)
                    endDay = self.setTimeFormat(datetime.today(), haveSeparator=False)
                    logger.info(f"GetStockInfo - getTickerKOSDAQ; startDay : {startDay}, endDay : {endDay}")
                    tmpData = stock.get_market_fundamental(
                        startDay,
                        endDay,
                        stockID, freq="d")

                    if not tmpData.empty:
                        self.infoTickerKOSDAQ[stockID] = tmpData
                        break
                except:pass
                time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)
            else:
                logger.critical(f"GetStockInfo - getTickerKOSDAQ; Empty Dataframe, ticker : {stockID}")
        logger.info(f"GetStockInfo - getTickerKOSDAQ; getTicker Total data length : {len(self.infoTickerKOSDAQ)}")


    def getBasicKOSPI(self, listKOSPI: list):
        logger.info("GetStockInfo - getBasicKOSPI")
        for stockID in listKOSPI:

            for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
                try:
                    startDay = self.setTimeFormat(CF.getStartFetchingDate(datetime.now()), haveSeparator=False)
                    endDay = self.setTimeFormat(datetime.today(), haveSeparator=False)
                    logger.info(f"GetStockInfo - getBasicKOSPI; startDay : {startDay}, endDay : {endDay}")
                    tmpData = stock.get_market_ohlcv_by_date(
                        fromdate=startDay,
                        todate=endDay,
                        ticker=stockID,
                        name_display=False
                    )

                    if not tmpData.empty:
                        self.infoBasicKOSPI[stockID] = tmpData
                        break

                except:pass
                time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)
            else:
                logger.critical(f"GetStockInfo - getBasicKOSPI; Empty Dataframe, ticker : {stockID}")
        logger.info(f"GetStockInfo - getBasicKOSPI; getBasic Total data length : {len(self.infoBasicKOSPI)}")



    def getTickerKOSPI(self, listKOSPI: list):
        logger.info("GetStockInfo - getTickerKOSPI")
        for stockID in listKOSPI:

            for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
                try:
                    startDay = self.setTimeFormat(CF.getStartFetchingDate(datetime.now()), haveSeparator=False)
                    endDay = self.setTimeFormat(datetime.today(), haveSeparator=False)
                    logger.info(f"GetStockInfo - getTickerKOSPI; startDay : {startDay}, endDay : {endDay}")
                    tmpData = stock.get_market_fundamental(
                        startDay,
                        endDay,
                        stockID, freq="d",
                    )
                    if not tmpData.empty:
                        self.infoTickerKOSPI[stockID] = tmpData
                        break

                except:pass
                time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)
            else:
                logger.critical(f"GetStockInfo - getTickerKOSPI; Empty Dataframe, ticker : {stockID}")
        logger.info(f"GetStockInfo - getTickerKOSPI; getTicker Total data length : {len(self.infoTickerKOSPI)}")


    def getBasicINDEX(self, listINDEX: list):
        logger.info("GetStockInfo - getBasicINDEX")
        for stockID in listINDEX:

            for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
                try:
                    startDay = self.setTimeFormat(CF.getStartFetchingDate(datetime.now()), haveSeparator=False)
                    endDay = self.setTimeFormat(datetime.today(), haveSeparator=False)
                    logger.info(f"GetStockInfo - getBasicINDEX; startDay : {startDay}, endDay : {endDay}")
                    tmpData = stock.get_index_ohlcv(
                        fromdate=startDay,
                        todate=endDay,
                        ticker=stockID,
                        name_display=False
                    )

                    if not tmpData.empty:
                        self.infoBasicINDEX[stockID] = tmpData
                        break

                except:pass
                time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)
            else:
                logger.critical(f"GetStockInfo - getBasicINDEX; Empty Dataframe, ticker : {stockID}")
        logger.info(f"GetStockInfo - getBasicINDEX; getBasic Total data length : {len(self.infoBasicINDEX)}")



    def getTickerINDEX(self, listINDEX: list):
        logger.info("GetStockInfo - getTickerINDEX")
        for stockID in listINDEX:

            for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
                try:
                    startDay = self.setTimeFormat(CF.getStartFetchingDate(datetime.now()), haveSeparator=False)
                    endDay = self.setTimeFormat(datetime.today(), haveSeparator=False)
                    logger.info(f"GetStockInfo - getTickerINDEX; startDay : {startDay}, endDay : {endDay}")
                    tmpData = stock.get_index_fundamental(
                        startDay,
                        endDay,
                        stockID, freq="d",
                    )
                    if not tmpData.empty:
                        self.infoTickerINDEX[stockID] = tmpData
                        break

                except:pass
                time.sleep(CONF.SLEEP_SECONDS_BETWEEN_RQ)
            else:
                logger.critical(f"GetStockInfo - getTickerINDEX; Empty Dataframe, ticker : {stockID}")
        logger.info(f"GetStockInfo - getTickerINDEX; getTicker Total data length : {len(self.infoTickerINDEX)}")


    def setTimeFormat(self, datetimeObject, haveSeparator=True):
        if haveSeparator:
            return datetimeObject.strftime("%Y-%m-%d")
        else:
            return datetimeObject.strftime("%Y%m%d")


def FinaceInformation(market=None, timeoutSeconds=2):
    """
    Dropbox 이용하여 해결, 마지막 dl=1 붙여 강제 다운로드 값 주기
    """
    sector_KS = \
        pd.read_csv(
            #'https://cvws.icloud-content.com/B/ASF24cjQqIR0KyVIGry56S5_GB6MASuBhHf2pM2dhZU6KifcuIBRTbyt/dataKOSPI.csv?o=ApbjL8zgqtVjZ_Vnr6JnE7iMQ9WZ8xg0gt0eYzRtlYpF&v=1&x=3&a=CAogH_oag-4nGVKDlEYCLcVy8AYmh6dnU-5M1TOpvbWSW9YSbxDgmfCt3y8Y4PbLr98vIgEAUgR_GB6MWgRRTbytaidmOfB-a1PXJcuofAO_LGsiyPr0h9e6xf5GDUNc_sf0pGvF1_fgsqJyJ4qL4agFzKiAfKqF2EcW-ly9ZcTF6mhGh6eiN6k_WQZCr0kc_P8A-g&e=1640508881&fl=&r=d370657d-df13-446a-8b32-210cee0f2123-1&k=fEMp0tm8XTL9SfcfkEGjlw&ckc=com.apple.clouddocs&ckz=com.apple.CloudDocs&p=38&s=r7MYuZgGUGIVrh5XiNzO8LAHdVs&%20=8c007e5e-4e93-4228-a8d4-7136bf84e99a',
            'https://www.dropbox.com/s/74pm86ir7xexlsu/dataKOSPI.csv?dl=1',
            encoding='EUC-KR',
            error_bad_lines=False
        )

    sector_KQ = \
        pd.read_csv(
            #'https://cvws.icloud-content.com/B/AVy50wk61JGh1RoSuSKQ3qsPcH0gAQlcesOBnd5Nlqz1GLD5MO-NQgNh/dataKOSDAQ.csv?o=Aqq6TDrBDXo0y0mFKv42XK9f7ON9DWjVBPuuOF6xJ40g&v=1&x=3&a=CAogW8MNWcEf5z1QJMKkQP1_b9hJCmvsJu-eVsGIz0LhWRkSbxC42vOt3y8YuLfPr98vIgEAUgQPcH0gWgSNQgNhaieuypEwCop_E3Qp_YkhoiwkZvECwM9-hNttMRldpo76v8pFeIUxLEtyJzqGd-F-ES_K4Q4Lt7TtQgJ3ByS4ku9NfAj8AQAQbP48puhnM6d71g&e=1640508939&fl=&r=a9b696e6-1c2f-4887-a5d5-f9605ef61e9a-1&k=1Cwpy-cjna_CaQ0XdK3KVQ&ckc=com.apple.clouddocs&ckz=com.apple.CloudDocs&p=38&s=6nZcFR8bxNWOEcVjErqbSbAgVyI&%20=0f1848a0-6188-4d15-8a03-f767d2fce49d',
            'https://www.dropbox.com/s/fsld76e20523yjo/dataKOSDAQ.csv?dl=1',
            encoding='EUC-KR',
            error_bad_lines=False
        )

    tmpData = sector_KS.append(sector_KQ)
    if isinstance(tmpData, pd.DataFrame) and '업종명' in tmpData:
        logger.critical("FinaceInformation - Dataframe is obtained")
    else:
        logger.critical("FinaceInformation - Dataframe is not obtained")
    return tmpData


def FinaceInformation2(market=None, timeoutSeconds=2):
    # https://wg-cy.tistory.com/54?category=1000874

    # 헤더 부분에 리퍼러(Referer)를 추가, 링크를 통해서 각각의 웹사이트로 방문할 때 남는 흔적입니다. (로봇으로 인식을 하지 않게 하기 위함.)
    headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}

    tmpKOSPI = CONF.KRX__GEN_OPT_DATA_KOSPI
    tmpKOSPI['trdDd'] = datetime.today().strftime("%Y%m%d")
    # otp = rq.post(CONF.KRX__GEN_OPT_URL, tmpKOSPI, headers=headers, timeout=timeoutSeconds).text
    # otp = rq.post("https://webhook.site/8ffea47b-1e4b-4c60-b135-eca191393c96", tmpKOSPI, headers=headers, timeout=timeoutSeconds).text
    otp = 'a1n6kaOi+6ccSQWhSJQn6bW/0lpfBRk5S+zXZdMA4aURtSksuLS7Bnxpl86F7dAOkunw9BBwugQaSjGAcH15ee4rg6nj43HicYMcso3v4LstBgM+EFJCxYg3zco1gIgRZqIo4cIzoURnTI8+MmkJ4m8vFLhSKmM794gFu+ThsO31lY4woqehX8j6OlXFDcfHdV4NbYo4+D2Rwcfj24VnU3Zpq3ik/Dyw3FdyOXhJkBI='
    #print(f'otp1 : {otp}')
    # https://webhook.site/8ffea47b-1e4b-4c60-b135-eca191393c96
    # download.cmd 에서 General의 Request URL 부분
    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    down_sector_KS = rq.post(down_url, {'code': otp}, headers=headers, timeout=timeoutSeconds)
    sector_KS = pd.read_csv(BytesIO(down_sector_KS.content), encoding='EUC-KR')
    # print(f'sector_KS : {sector_KS.head(10)}')

    tmpKOSDAQ = CONF.KRX__GEN_OPT_DATA_KOSDAQ
    tmpKOSDAQ['trdDd'] = datetime.today().strftime("%Y%m%d")
    # otp = rq.post(CONF.KRX__GEN_OPT_URL, tmpKOSDAQ, headers=headers, timeout=timeoutSeconds).text
    #print(f'otp2 : {otp}')
    down_sector_KQ = rq.post(down_url, {'code': otp}, headers=headers, timeout=timeoutSeconds)
    sector_KQ = pd.read_csv(BytesIO(down_sector_KQ.content), encoding='EUC-KR')
    # print(f'sector_KQ : {sector_KQ.head(10)}')

    tmpData = sector_KS.append(sector_KQ)

    print(f'tmpData.head(10) : {tmpData.head(10)}')
    if isinstance(tmpData, pd.DataFrame) and '업종명' in tmpData:
        logger.info("FinaceInformation - Dataframe is obtained")
    return tmpData


if __name__ == '__main__':
    pass

"""
# PER
'forwardPE'
# PBR

# ROE
'returnOnEquity'
# ROA
'returnOnAssets'
# industry
'industry'
# sector
'sector'

    # def getYahooKOSDAQ(self, listKOSDAQ:list):
    #     for stockID in listKOSDAQ:
    #         try:
    #             tmpData = yf.Ticker(
    #                 stockID+".KQ",
    #             )
    #             self.infoYahooKOSDAQ[stockID] = tmpData
    #         except:pass

"""
