from django.db.models import Q, F
from appStockInfo.models import (
    StockTick,
    StockItemListName,
    StockItem,
    StockSection,
    StockLastUpdateTime
)
import ConfigFile as CONF

from pykrx import stock
# import yfinance

from datetime import datetime, timedelta
import pandas as pd
import requests as rq
from io import BytesIO
import traceback

class MainWrapperKR:

    def __init__(self):

        self.stockList = GetStockList()
        self.stockInfo = GetStockInfo()

    def doAction(self):
        self.stockList.doAction()
        self.stockInfo.doAction(self.stockList.KOSPI, self.stockList.KOSDAQ)

        # CRUD
        # 1) Create StockTick
        self.createStockTick(self.stockList.KOSPI, "KOSPI")
        self.createStockTick(self.stockList.KOSDAQ, "KOSDAQ")

        # 2) Create StockItemListName
        self.createStockItemListName(self.stockList.KOSPI, "KOSPI")
        self.createStockItemListName(self.stockList.KOSDAQ, "KOSDAQ")

        # 3) Create StockSection
        self.createStockSection()

        # 4-1) Delete StockItems
        self.deleteStockItem()
        # 4-2) Create StockItems
        self.createStockItem(self.stockList.KOSPI, "KOSPI")
        self.createStockItem(self.stockList.KOSDAQ, "KOSDAQ")

        # 5) Create DateStamp
        self.updateStockLastUpdateTime()


    def createStockTick(self, listStocks:list, marketName:str='Dummy' ):
        """
        create ticker CRUD
        > if info is not provided, set to False
        > if Ticker doesn't exist, add

        [ORM]
        stock_tick : Stock 코드
        stock_marketName : 등록된 마켓 이름
        stock_isInfoAvailable : Fetch된 market 데이터 존재하는 경우
            -> StockItem 등록시, 데이터 없으면 False로 다시 세팅
        """

        StockTick.objects.all().update(stock_isInfoAvailable=False)
        exsist_stocktick = StockTick.objects.all().values_list('stock_tick', flat=True)

        update_exist_stocktick = set(exsist_stocktick) & set(listStocks)
        create_new_stocktick = set(listStocks) - set(exsist_stocktick)

        # update existing stock
        filter_1 = StockTick.objects.filter(stock_tick__in=update_exist_stocktick)
        filter_1.update(stock_isInfoAvailable=True)

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


    def createStockItemListName(self, listStocks:list, marketName:str='Dummy'):
        """
        create ticker to name CRUD
        > if Ticker exists, and Name isNot provided, it will be replaced with a ticker

        [ORM]
        stock_tick : ForeignKey - Stock 코드
        stock_name : 실제 종목 이름 Mapping 값
        """

        exsist_stocktick = StockItemListName.objects.all().values_list('stock_tick', flat=True)
        create_new_stocktick = set(listStocks) - set(exsist_stocktick)

        # create new stock list item
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
                if tmpStockTick.exists(): # 존재한다면
                    filter_2.append(
                        StockItemListName(
                            stock_tick=tmpStockTick.first(),
                            stock_name=tmpNameData
                        )
                    )
                else: # 존재하지 않는다면, create 이후 업데이트
                    tmpCreateStockTick = StockTick(
                        stock_tick=stock_tick,
                        stock_marketName=marketName,
                        stock_isInfoAvailable=False
                    )
                    filter_1.append(tmpCreateStockTick)
                    filter_2.append(
                        StockItemListName(
                            stock_tick=tmpCreateStockTick,
                            stock_name=tmpNameData
                        )
                    )
            except:pass

        StockTick.objects.bulk_create(filter_1)
        StockItemListName.objects.bulk_create(filter_2)


    def createStockSection(self):
        """
        Stock Sections mapping
        > Non existing will be added

        [ORM]
        if Relational Field doesn't exist in the table, return others
        -> create "Others"
        """
        tmpOthers = StockSection.objects.filter(section_name="Others")
        if not tmpOthers.exists():
            StockSection.objects.create(
                section_name="Others"
            )

        tmpStockSectionDF = self.stockInfo.infoFinanceData
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


    def deleteStockItem(self):

        # 모든것을 지움
        StockItem.objects.all().delete()

    def createStockItem(self, listStocks:list, market):
        """
        create Stock information CRUD
        > 1) If StockName exists : Needs Update if StockTick is True
        > 2) If StockName doesn't exists: Skip
        [ORM]
        stock_tick : ForeignKey - Stock 코드
        stock_name : 실제 종목 이름 Mapping 값
        """
        #exsist_stocktick = StockItemListName.objects.filter(stock_tick__stock_isInfoAvailable=True)

        assert(market in ["KOSPI", "KOSDAQ"])



        # 정보 lookup 세팅
        filter_1 = []
        infoFinanceDF = self.stockInfo.infoFinanceData
        if infoFinanceDF.isnull().values.any():
            print(f'infoFinanceDF : \n{infoFinanceDF.head(10)}')

        # total iteration
        for tick in listStocks:
            try:

                # pull from Info
                if market == "KOSPI":
                    tmpInfoBasic = self.stockInfo.infoBasicKOSPI[tick]
                    tmpTickerBasic = self.stockInfo.infoTickerKOSPI[tick]
                elif market == "KOSDAQ":
                    tmpInfoBasic = self.stockInfo.infoBasicKOSDAQ[tick]
                    tmpTickerBasic = self.stockInfo.infoTickerKOSDAQ[tick]

                # Dataframe prep
                concatDF = pd.concat(
                    [
                        tmpInfoBasic,
                        tmpTickerBasic
                    ], axis=1
                )
                concatDF['ROE'] = concatDF['EPS']/concatDF['BPS'] * 100
                concatDF['시가총액'] = int(
                    infoFinanceDF.loc[infoFinanceDF['종목코드'] == tick, "시가총액"].values[0]
                )

                # -> Nan value removal
                # https://rfriend.tistory.com/542
                # https://rfriend.tistory.com/262
                fill_missing_nan = {
                    'ROE' : 0,
                    '거래량': 0,
                    'BPS' : concatDF['BPS'].bfill(),
                    'PER' : concatDF['PER'].bfill(),
                    'PBR' : concatDF['PBR'].bfill(),
                    'EPS' : concatDF['EPS'].bfill(),
                    'DIV' : concatDF['DIV'].bfill()
                }
                concatDF.fillna(fill_missing_nan, inplace=True) # removal inplace


                # get StockSection object
                try: # 없으면 Other 할당
                    #section = str(selectedDF["업종명"])
                    section = str(
                        infoFinanceDF.loc[infoFinanceDF['종목코드'] == tick, '업종명'].values[0]
                    )
                except: section = str("Other")


                # Foreign Key
                tmpStockName = StockItemListName.objects.get(
                    stock_tick=tick
                )
                tmpSectionName = StockSection.objects.get(
                    section_name=section
                )

                # iteration
                for idx, row in concatDF.iterrows():
                    reg_date = idx
                    open = row["시가"]
                    high = row["고가"]
                    low = row["저가"]
                    close = row["종가"]
                    volume = row["거래량"]
                    total_sum = row["시가총액"]
                    div = row["DIV"]
                    per = row["PER"]
                    pbr = row["PBR"]
                    roe = row["ROE"]
                    filter_1.append(
                        StockItem(
                            stock_name=tmpStockName,
                            section_name=tmpSectionName,
                            reg_date=reg_date,
                            open=open,
                            high=high,
                            low=low,
                            close=close,
                            volume=volume,
                            total_sum=total_sum,
                            div=div,
                            per=per,
                            pbr=pbr,
                            roe=roe
                        )
                    )
            except Exception as e: pass

        StockItem.objects.bulk_create(filter_1)


    def updateStockLastUpdateTime(self):
        """
        update dateime of last update of KR stocks
        """
        StockLastUpdateTime.objects.create()


class GetStockList:
    def __init__(self):
        self.KOSDAQ = None
        self.KOSPI = None
        self.tickerToName = {}

    def doAction(self):
        self.getMarketTickers()
        self.getTickerNameKOSDAQ()
        self.getTickerNameKOSPI()

    def getMarketTickers(self):
        self.KOSDAQ = list(set(stock.get_market_ticker_list(market="KOSDAQ")))
        self.KOSPI = list(set(stock.get_market_ticker_list(market="KOSPI")))


    def getTickerNameKOSDAQ(self):
        for stockTicker in self.KOSDAQ:
            try:
                self.tickerToName[stockTicker] = stock.get_market_ticker_name(stockTicker)
            except:
                self.tickerToName[stockTicker] = stockTicker

    def getTickerNameKOSPI(self):
        for stockTicker in self.KOSPI:
            try:
                self.tickerToName[stockTicker] = stock.get_market_ticker_name(stockTicker)
            except:
                self.tickerToName[stockTicker] = stockTicker

    def __str__(self) -> str:
        return f'KOSDAQ : \n {self.KOSDAQ[:10]}  \nKOSPI : \n {self.KOSPI[:10]}'


class GetStockInfo:
    TOTAL_REQUEST_DATE_LENGTH = CONF.TOTAL_REQUEST_DATE_LENGTH

    def __init__(self):
        self.infoBasicKOSDAQ = {}
        self.infoBasicKOSPI = {}
        self.infoTickerKOSDAQ = {}
        self.infoTickerKOSPI = {}

        self.infoFinanceData = None

    def doAction(self, listKOSPI:list, listKOSDAQ:list):
        self.getBasicKOSPI(listKOSPI)
        self.getTickerKOSPI(listKOSPI)

        self.getBasicKOSDAQ(listKOSDAQ)
        self.getTickerKOSDAQ(listKOSDAQ)

        self.getFinanceData()

    def getFinanceData(self):
        """업종 데이터"""
        tmpData =  FinaceInformation("KRX")
        self.infoFinanceData = tmpData

    def getBasicKOSDAQ(self, listKOSDAQ:list):

        for stockID in listKOSDAQ:

            try:
                tmpData = stock.get_market_ohlcv_by_date(
                    fromdate=self.setTimeFormat(self.createStartDate(), haveSeparator=False),
                    todate=self.setTimeFormat(datetime.today(), haveSeparator=False),
                    ticker=stockID,
                    name_display=False
                )

                self.infoBasicKOSDAQ[stockID] = tmpData
            except:pass


    def getTickerKOSDAQ(self, listKOSDAQ:list):
        for stockID in listKOSDAQ:
            try:
                tmpData = stock.get_market_fundamental(
                                                       self.setTimeFormat(self.createStartDate(), haveSeparator=False),
                                                       self.setTimeFormat(datetime.today(), haveSeparator=False),
                                                       stockID, freq="d")
                self.infoTickerKOSDAQ[stockID] = tmpData
            except:pass



    def getBasicKOSPI(self, listKOSPI:list):

        for stockID in listKOSPI:
            try:
                tmpData = stock.get_market_ohlcv_by_date(
                    fromdate=self.setTimeFormat(self.createStartDate(), haveSeparator=False),
                    todate=self.setTimeFormat(datetime.today(), haveSeparator=False),
                    ticker=stockID,
                    name_display=False
                )

                self.infoBasicKOSPI[stockID] = tmpData
            except:pass

    def getTickerKOSPI(self, listKOSPI:list):
        for stockID in listKOSPI:
            try:
                tmpData = stock.get_market_fundamental(
                                                       self.setTimeFormat(self.createStartDate(), haveSeparator=False),
                                                       self.setTimeFormat(datetime.today(), haveSeparator=False),
                                                       stockID, freq="d",
                                                       )
                self.infoTickerKOSPI[stockID] = tmpData
            except:pass


    def createStartDate(self, normDate=datetime.today()):
        return normDate - timedelta(days=GetStockInfo.TOTAL_REQUEST_DATE_LENGTH)

    def setTimeFormat(self, datetimeObject, haveSeparator=True):
        if haveSeparator:
            return datetimeObject.strftime("%Y-%m-%d")
        else:
            return datetimeObject.strftime("%Y%m%d")


def FinaceInformation(market=None):
    # https://wg-cy.tistory.com/54?category=1000874

    # 헤더 부분에 리퍼러(Referer)를 추가, 링크를 통해서 각각의 웹사이트로 방문할 때 남는 흔적입니다. (로봇으로 인식을 하지 않게 하기 위함.)
    headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}

    tmpKOSPI = CONF.KRX__GEN_OPT_DATA_KOSPI
    tmpKOSPI['trdDd'] = datetime.today().strftime("%Y%m%d")
    otp = rq.post(CONF.KRX__GEN_OPT_URL, tmpKOSPI, headers=headers).text
    # download.cmd 에서 General의 Request URL 부분
    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    down_sector_KS = rq.post(down_url, {'code': otp}, headers=headers)
    sector_KS = pd.read_csv(BytesIO(down_sector_KS.content), encoding='EUC-KR')

    tmpKOSDAQ = CONF.KRX__GEN_OPT_DATA_KOSDAQ
    tmpKOSDAQ['trdDd'] = datetime.today().strftime("%Y%m%d")
    otp = rq.post(CONF.KRX__GEN_OPT_URL, tmpKOSDAQ, headers=headers).text
    down_sector_KQ = rq.post(down_url, {'code': otp}, headers=headers)
    sector_KQ = pd.read_csv(BytesIO(down_sector_KQ.content), encoding='EUC-KR')

    tmpData = sector_KS.append(sector_KQ)
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