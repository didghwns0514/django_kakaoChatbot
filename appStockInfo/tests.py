import unittest

from django.test import TestCase
from appStockInfo.job.interface.KR.Wrapper import (
    GetStockInfo, GetStockList
)
from datetime import datetime, timedelta
import time

# Create your tests here.
class GetStockListTest(TestCase):
    def test_GetStockList(self):
        stockList = GetStockList()
        totalList = stockList.KOSDAQ + stockList.KOSPI

        print(f'len(stockList.KOSDAQ) : {len(stockList.KOSDAQ)}')
        print(f'len(stockList.KOSPI) : {len(stockList.KOSPI)}')
        print(stockList)

        self.assertGreater(len(totalList), 2000)

    @unittest.skip
    def test_getTickerNameKOSDAQ(self):
        stockList = GetStockList()
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

    @unittest.skip
    def test_getBasicKOSDAQ(self):
        stockList = GetStockList()
        stockInfo = GetStockInfo()
        startTime = time.time()
        stockInfo.getBasicKOSDAQ(stockList.KOSDAQ)
        endTime = time.time() - startTime
        print(f'elapsed time : {endTime}')

    @unittest.skip
    def test_getTickerKOSDAQ(self):
        stockList = GetStockList()
        stockInfo = GetStockInfo()
        startTime = time.time()
        stockInfo.getTickerKOSDAQ(stockList.KOSDAQ)
        endTime = time.time() - startTime
        print(f'elapsed time : {endTime}')

    def test_getTickerKOSDAQ_SAMSUNG(self):
        stockList = GetStockList()
        stockInfo = GetStockInfo()
        startTime = time.time()
        stockInfo.getTickerKOSPI(stockList.KOSPI)
        endTime = time.time() - startTime
        print(f'elapsed time : {endTime}')

        tickerSamsung = "005930.KS"
        print(f'ticker to Name : {stockList.tickerToName[tickerSamsung]}')
        print(f'ticker Dataframe : {stockInfo.infoBasicKOSPI[tickerSamsung]}')
        print(f'ticker info : {stockInfo.infoTickerKOSPI[tickerSamsung].info}')