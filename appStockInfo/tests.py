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

        print(stockList)

        self.assertGreater(len(totalList), 2000)

class GetStockInfoTest(TestCase):

    def test_setTimeFormat(self):
        stockInfo = GetStockInfo()

        self.assertEquals(
            stockInfo.setTimeFormat(datetime(2019,5,14)),
            '2019-05-14'
        )

    def test_getBasicKOSDAQ(self):
        stockList = GetStockList()
        stockInfo = GetStockInfo()
        startTime = time.time()
        stockInfo.getBasicKOSDAQ(stockList.KOSDAQ)
        endTime = time.time()-startTime
        print(f'elapsed time : {endTime}')
