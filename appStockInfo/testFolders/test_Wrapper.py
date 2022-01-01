import unittest

from django.test import TestCase
from appStockInfo.job.interface.KR.Wrapper import (
    GetStockInfo, GetStockList, MainWrapperKR
)
from datetime import datetime, timedelta
import time

# Create your tests here.
class GetStockListTest(TestCase):

    #@unittest.skip
    def test_GetStockList(self):
        stockList = GetStockList()
        stockList.getMarketTickers()
        totalList = stockList.KOSDAQ + stockList.KOSPI

        print(f'len(stockList.KOSDAQ) : {len(stockList.KOSDAQ)}')
        print(f'len(stockList.KOSPI) : {len(stockList.KOSPI)}')
        print(stockList)

        self.assertGreater(len(totalList), 2000)

    @unittest.skip
    def test_getTickerNameKOSDAQ(self):
        stockList = GetStockList()
        stockList.doAction()
        tickerNames = stockList.tickerToName

        for ticker in list(tickerNames.keys())[:10]:
            print(f'ticker : {ticker}  // name : {tickerNames[ticker]}')


class GetStockInfoTest(TestCase):

    def test_setTimeFormat(self):
        stockInfo = GetStockInfo()

        self.assertEquals(
            stockInfo.setTimeFormat(datetime(2019,5,14)),
            '2019-05-14'
        )

    @unittest.skip("Functionality test - Pass/Long")
    def test_getBasicKOSDAQ(self):
        stockList = GetStockList()
        stockInfo = GetStockInfo()
        startTime = time.time()
        stockInfo.getBasicKOSDAQ(stockList.KOSDAQ)
        endTime = time.time() - startTime
        print(f'elapsed time : {endTime}')

    @unittest.skip("Functionality test - Pass/Long")
    def test_getTickerKOSDAQ(self):
        stockList = GetStockList()
        stockInfo = GetStockInfo()
        startTime = time.time()
        stockInfo.getTickerKOSDAQ(stockList.KOSDAQ)
        endTime = time.time() - startTime
        print(f'elapsed time : {endTime}')

    @unittest.skip("Functionality test - Pass/Long")
    def test_getTickerKOSDAQ_SAMSUNG(self):
        stockList = GetStockList()
        stockInfo = GetStockInfo()
        startTime = time.time()
        stockInfo.getBasicKOSPI(stockList.KOSPI)
        stockInfo.getTickerKOSPI(stockList.KOSPI)
        endTime = time.time() - startTime
        print(f'elapsed time : {endTime}')

        tickerSamsung = "005930"
        print(f'ticker to Name : {stockList.tickerToName[tickerSamsung]}')
        print(f'ticker Dataframe : {stockInfo.infoBasicKOSPI[tickerSamsung]}')
        print(f'ticker info : {stockInfo.infoTickerKOSPI[tickerSamsung].info}')

        tickerHynix = "000660"
        print(f'ticker to Name : {stockList.tickerToName[tickerHynix]}')
        print(f'ticker Dataframe : {stockInfo.infoBasicKOSPI[tickerHynix]}')
        print(f'ticker info : {stockInfo.infoTickerKOSPI[tickerHynix].info}')

    @unittest.skip("Functionality test - Pass")
    def test_pykrxTicker(self):
        from pykrx import stock
        import yfinance as yf

        tickerHynix = "000660"
        startDate = "20210311"
        startDate2 = "2021-03-11"
        endDate = "20210321"
        endDate2 = "2021-03-21"
        tmpMarketData = stock.get_market_fundamental(
                                               startDate,
                                               endDate,
                                               tickerHynix, freq="d")
        print(f'tmpMarketData : {tmpMarketData}')

        tmpStockData = yf.download(
            tickerHynix + ".KS",
            start=startDate2,
            end=endDate2,
            timeout=1,
            progress=False,
            show_errors=False,
            threads=False
        )

        print(f'tmpStockData : {tmpStockData}')

    @unittest.skip("Data generation done - Pass")
    def test_mockDataGeneration(self):
        import pickle, os
        from pathlib import Path

        print(f'Start mock data generation!')
        root = Path(__file__).resolve().parent.parent

        stockList = GetStockList()
        stockList.doAction()
        print(f'Finished mock data GetStockList!')

        stockInfo = GetStockInfo()
        stockInfo.doAction(stockList.KOSPI, stockList.KOSDAQ)
        print(f'Finished mock data GetStockInfo!')

        startTime = time.time()
        with open(
                os.path.join(
                    root,
                    'testMockData', 'stockList.p'
                ), 'wb') as f:
            pickle.dump(stockList, f)
            print(f'successful StockList class save')

        with open(
                os.path.join(
                    root,
                    'testMockData', 'stockInfo.p'
                ), 'wb') as f:
            pickle.dump(stockInfo, f)
            print(f'successful StockInfo class save')

        endTime = time.time() - startTime
        print(f'total execution time : {endTime}')

    def test_getFinanceData(self):
        getStockInfo = GetStockInfo()
        getStockInfo.getFinanceData()

        print(f'finance data obtained : \n{getStockInfo.infoFinanceData.head(10)}')
        self.assertEquals(
            getStockInfo.infoFinanceData.empty, False
        )

class GetScheduler(TestCase):

    IS_SUCCESS = False

    @unittest.skip("Apscheduler functionality test done - Pass")
    def test_taskStockKR(self):
        from apscheduler.schedulers.background import BackgroundScheduler
        from datetime import datetime, timedelta


        def test_function():
            global isSuccess
            print(f'test_function is called!')
            GetScheduler.IS_SUCCESS = True

        deltaSeconds = 2
        dateNow = datetime.now()
        dateMoved = dateNow + timedelta(seconds=deltaSeconds)
        scheduler = BackgroundScheduler(timezone="Asia/Seoul")
        scheduler.add_job(test_function,
                          'cron',
                          id="test_job",
                          hour=str(dateMoved.hour),
                          minute=str(dateMoved.minute),
                          second=str(dateMoved.second)
                          )
        scheduler.start()

        startTime = time.time()
        while True and (time.time() - startTime < 5 + 2):
            if GetScheduler.IS_SUCCESS == True:
                break

        self.assertEquals(GetScheduler.IS_SUCCESS, True)

