from pykrx import stock
from datetime import datetime, timedelta
import yfinance as yf


class MainWrapper:

    def __init__(self):

        self.stockList = GetStockList()
        self.stockInfo = GetStockInfo()

    def doAction(self):
        self.stockList.doAction()
        self.stockInfo.doAction(self.stockList.KOSPI, self.stockList.KOSDAQ)

    def createStockTick(self, listStocks ):
        """
        create ticker CRUD
        > if info is not provided, set to False
        > if Ticker doesn't exist, add
        """
        pass

    def createMapTickerToName(self):
        """
        create ticker to name CRUD
        > if Ticker exists, and Name isNot provided, it will be replaced with a ticker
        """
        pass

class GetStockList:
    def __init__(self):
        self.KOSDAQ = list(set(stock.get_market_ticker_list(market="KOSDAQ")))
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
    TOTAL_REQUEST_DATE_LENGTH = 10

    def __init__(self):
        self.infoBasicKOSDAQ = {}
        self.infoBasicKOSPI = {}
        self.infoTickerKOSDAQ = {}
        self.infoTickerKOSPI = {}
        self.infoYahooKOSDAQ = {}
        self.infoYahooKOSPI = {}

    def doAction(self, listKOSPI:list, listKOSDAQ:list):
        self.getBasicKOSPI(listKOSPI)
        self.getTickerKOSPI(listKOSPI)
        self.getYahooKOSPI(listKOSPI)
        self.getBasicKOSDAQ(listKOSDAQ)
        self.getTickerKOSDAQ(listKOSDAQ)
        self.getYahooKOSDAQ(listKOSDAQ)


    def getBasicKOSDAQ(self, listKOSDAQ:list):

        for stockID in listKOSDAQ:

            try:
                tmpData = yf.download(
                    stockID + ".KQ",
                    start=self.setTimeFormat(self.createStartDate()),
                    timeout=1,
                    progress=False,
                    show_errors=False,
                    threads=False,

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

    def getYahooKOSDAQ(self, listKOSDAQ:list):
        for stockID in listKOSDAQ:
            try:
                tmpData = yf.Ticker(
                    stockID+".KQ",
                )
                self.infoYahooKOSDAQ[stockID] = tmpData
            except:pass

    def getBasicKOSPI(self, listKOSPI:list):

        for stockID in listKOSPI:
            try:
                tmpData = yf.download(
                    stockID + ".KS",
                    start=self.setTimeFormat(self.createStartDate()),
                    timeout=1,
                    progress=False,
                    show_errors=False,
                    threads=False
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

    def getYahooKOSPI(self, listKOSPI:list):
        for stockID in listKOSPI:
            try:
                tmpData = yf.Ticker(
                    stockID+".KS",
                )
                self.infoYahooKOSPI[stockID] = tmpData
            except:pass

    def createStartDate(self, normDate=datetime.today()):
        return normDate - timedelta(days=GetStockInfo.TOTAL_REQUEST_DATE_LENGTH)

    def setTimeFormat(self, datetimeObject, haveSeparator=True):
        if haveSeparator:
            return datetimeObject.strftime("%Y-%m-%d")
        else:
            return datetimeObject.strftime("%Y%m%d")

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
"""