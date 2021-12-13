from django.db.models import Q, F
from appStockInfo.models import (
    StockTick,
    StockItemListName,
    StockItem
)
import ConfigFile as CONF

from pykrx import stock
# import yfinance

from datetime import datetime, timedelta
import pandas as pd
import requests as rq
from io import BytesIO


class MainWrapper:

    def __init__(self):

        self.stockList = GetStockList()
        self.stockInfo = GetStockInfo()

    def doAction(self):
        self.stockList.doAction()
        self.stockInfo.doAction(self.stockList.KOSPI, self.stockList.KOSDAQ)

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

        for tick in listStocks:
            stockTickFilter = StockTick.objects.filter(stock_tick=tick)
            if not stockTickFilter: # Not existing in DB
                StockTick.objects.create(
                    stock_tick=str(tick),
                    stock_marketName=marketName,
                    stock_isInfoAvailable=True
                )
            else: # Already in DB
                stockTickFilter.update(stock_isInfoAvailable=True)


    def createStockItemListName(self, listStocks:list, marketName:str='Dummy'):
        """
        create ticker to name CRUD
        > if Ticker exists, and Name isNot provided, it will be replaced with a ticker

        [ORM]
        stock_tick : ForeignKey - Stock 코드
        stock_name : 실제 종목 이름 Mapping 값
        """
        for tick in listStocks:
            stockTickFilter = StockItemListName.objects.filter(stock_tick=tick)
            if tick not in self.stockList.tickerToName:
                tmpNameData = str(tick)
            else:
                tmpNameData = self.stockList.tickerToName[tick]
            if not stockTickFilter: # Not existing in DB
                tmpStockTick = StockTick.objects.filter(
                        stock_tick=tick,
                        # stock_marketName=marketName,
                        # stock_isInfoAvailable=False
                    )
                if not tmpStockTick:
                    tmpStockTick = StockTick.objects.create(
                        stock_tick=tick,
                        stock_marketName=marketName,
                        stock_isInfoAvailable=False
                    )
                else:
                    tmpStockTick = StockTick.objects.get(stock_tick=tick)
                StockItemListName.objects.create(
                    stock_tick=tmpStockTick,
                    stock_name=tmpNameData
                )
            else: # Already in DB
                pass

    def createStockItem(self):
        pass

class GetStockList:
    def __init__(self):
        self.KOSDAQ = list(set(stock.get_market_ticker_list(
                                    market="KOSDAQ",

                                    )))
        self.KOSPI = list(set(stock.get_market_ticker_list(market="KOSPI")))
        self.tickerToName = {}

    def doAction(self):
        self.getTickerNameKOSDAQ()
        self.getTickerNameKOSPI()


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

    # generate.cmd에서 Request URL과 동일

    # generate.cmd에서 Form Data와 동일

    # 헤더 부분에 리퍼러(Referer)를 추가합니다.
    # 리퍼러란 링크를 통해서 각각의 웹사이트로 방문할 때 남는 흔적입니다. (로봇으로 인식을 하지 않게 하기 위함.)
    headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}

    otp = rq.post(CONF.KRX__GEN_OPT_URL, CONF.KRX__GEN_OPT_DATA_KOSPI, headers=headers).text
    # download.cmd 에서 General의 Request URL 부분
    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    down_sector_KS = rq.post(down_url, {'code': otp}, headers=headers)
    sector_KS = pd.read_csv(BytesIO(down_sector_KS.content), encoding='EUC-KR')


    otp = rq.post(CONF.KRX__GEN_OPT_URL, CONF.KRX__GEN_OPT_DATA_KOSDAQ, headers=headers).text
    down_sector_KQ = rq.post(down_url, {'code': otp}, headers=headers)
    sector_KQ = pd.read_csv(BytesIO(down_sector_KQ.content), encoding='EUC-KR')

    print(F'sector_KS : {sector_KS.head(10)}')
    print(f'type(sector_KS) : {type(sector_KS)}')
    print(f'len(sector_KS) : {len(sector_KS)}')
    print(F'sector_KQ : {sector_KQ.head(10)}')

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