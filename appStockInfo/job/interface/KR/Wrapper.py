from pykrx import stock
from datetime import datetime, timedelta
import yfinance as yf


class MainWrapper:

    def __init__(self):pass

class GetStockList:
    def __init__(self):
        self.KOSDAQ = stock.get_market_ticker_list(market="KOSDAQ")
        self.KOSPI = stock.get_market_ticker_list(market="KOSPI")

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
                    timeout=0.5,
                    progress=False,
                    show_errors=False,
                    threads=False
                )
                print(f'stockID - success : {stockID}')
                self.infoBasicKOSDAQ[stockID] = tmpData
            except:print(f'stockID - false : {stockID}')



    def getTickerKOSDAQ(self, listKOSDAQ:list):
        for stockID in listKOSDAQ:
            self.infoTickerKOSDAQ[stockID] = yf.Ticker(stockID+".KQ")

    def getBasicKOSPI(self, listKOSPI:list):

        for stockID in listKOSPI:
            tmpData = yf.download(
                stockID + ".KS",
                start=self.setTimeFormat(self.createStartDate()),
                timeout=0.2,
                threads=False
            )
            print(f'stockID : {stockID}')
            self.infoBasicKOSPI[stockID] = tmpData

    def getTickerKOSPI(self, listKOSPI:list):
        for stockID in listKOSPI:
            self.infoTickerKOSPI[stockID] = yf.download(
                stockID + ".KS",
                start=self.setTimeFormat(self.createStartDate())
            )

    def createStartDate(self):
        return datetime.today() - timedelta(days=GetStockInfo.TOTAL_REQUEST_DATE_LENGTH)

    def setTimeFormat(self, datetimeObject):
        return datetimeObject.strftime("%Y-%m-%d")


if __name__ == '__main__':
    pass