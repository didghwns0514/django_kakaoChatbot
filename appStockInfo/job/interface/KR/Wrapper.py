from pykrx import stock
from datetime import datetime, timedelta
import yfinance as yf


class MainWrapper:

    def __init__(self):

        self.stockList = GetStockList()
        self.stockInfo = GetStockInfo()

class GetStockList:
    def __init__(self):
        self.KOSDAQ = list(set(stock.get_market_ticker_list(market="KOSDAQ")))
        self.KOSPI = list(set(stock.get_market_ticker_list(market="KOSPI")))
        self.tickerToName = {}

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

    def getBasicKOSDAQ(self, listKOSDAQ:list):

        for stockID in listKOSDAQ:

            try:
                tmpData = yf.download(
                    stockID + ".KQ",
                    start=self.setTimeFormat(self.createStartDate()),
                    timeout=1,
                    progress=False,
                    show_errors=False,
                    threads=False
                )

                self.infoBasicKOSDAQ[stockID] = tmpData
            except:pass


    def getTickerKOSDAQ(self, listKOSDAQ:list):
        for stockID in listKOSDAQ:
            try:
                tmpData = yf.Ticker(
                    stockID+".KQ"

                )
                self.infoTickerKOSDAQ[stockID] = tmpData
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
                self.infoTickerKOSPI[stockID] = yf.download(
                    stockID + ".KS",
                    start=self.setTimeFormat(self.createStartDate())
                )
            except:pass

    def createStartDate(self):
        return datetime.today() - timedelta(days=GetStockInfo.TOTAL_REQUEST_DATE_LENGTH)

    def setTimeFormat(self, datetimeObject):
        return datetimeObject.strftime("%Y-%m-%d")


if __name__ == '__main__':
    pass