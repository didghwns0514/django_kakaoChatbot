import unittest

from django.test import TestCase
from appStockInfo.job.interface.KR.Wrapper import (
    GetStockInfo, GetStockList, MainWrapper
)

from appStockInfo.models import (
    StockTick,
    StockItemListName,
    StockItem
)
from appStockInfo.scheduler import taskStockUS, taskStockKR

class CreateKRStocks(TestCase):
    def test_createStockTick(self):
        import pickle, os
        import copy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        #print(f'root : {root}')
        mainWrapper = MainWrapper()

        with open(
                os.path.join(
                    root,
                    'testMockData', 'stockList.p'
                ), 'rb'
        ) as f:
            mainWrapper.stockList = copy.deepcopy(pickle.load(f))

        with open(
                os.path.join(
                    root,
                    'testMockData', 'stockInfo.p'
                ), 'rb'
        ) as f:
            mainWrapper.stockInfo = copy.deepcopy(pickle.load(f))

        # Test Model
        ## Add dummy
        StockTick.objects.create(
            stock_tick="000000",
            stock_marketName="testMarket",
            stock_isInfoAvailable=True
        )
        mainWrapper.createStockTick(
            mainWrapper.stockList.KOSPI, "KOSPI",
        )

        # check False for dummy
        tmpDummy = StockTick.objects.get(stock_tick="000000")
        self.assertEquals(tmpDummy.stock_isInfoAvailable,False)


    def test_createStockItemListName(self):
        import pickle, os
        import copy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        #  /Users/yanghojun/Library/Mobile Documents/com~apple~CloudDocs/Code_mac/vscode/app_StockManager/django_kakaoChatbot/appStockInfo
        mainWrapper = MainWrapper()

        with open(
                os.path.join(
                    root,
                    'testMockData', 'stockList.p'
                ), 'rb'
        ) as f:
            mainWrapper.stockList = copy.deepcopy(pickle.load(f))

        with open(
                os.path.join(
                    root,
                    'testMockData', 'stockInfo.p'
                ), 'rb'
        ) as f:
            mainWrapper.stockInfo = copy.deepcopy(pickle.load(f))

        # Test Model
        ## Add dummys
        dummy1_tick = "000000" # Added from StockTick
        dummy1_name = "testMarket_1"
        dummy2_tick = "000001" # Not included in StockTick
        dummy2_name = "testMarket_2"
        nameSpace= {
            dummy1_tick:dummy1_name,
            #dummy2_tick:dummy2_name
        }

        # Update records in Main Memory
        tmp_StockList = copy.deepcopy(mainWrapper.stockList.KOSPI)
        tmp_StockList.extend([dummy1_tick, dummy2_tick])
        mainWrapper.stockList.tickerToName.update(nameSpace)

        # Call Wrapper methods for CRUD
        StockTick.objects.create(
            stock_tick=dummy1_tick,
            stock_marketName=dummy1_name,
            stock_isInfoAvailable=True
        )
        mainWrapper.createStockTick(
            mainWrapper.stockList.KOSPI, "KOSPI",
        )
        mainWrapper.createStockItemListName(
            tmp_StockList
        )

        # check
        readDummy1 = StockItemListName.objects.get(stock_tick=dummy1_tick)
        readDummy2 = StockItemListName.objects.get(stock_tick=dummy2_tick)

        # assertions
        self.assertEqual(str(readDummy1.stock_name), dummy1_name)
        self.assertEqual(str(readDummy1.stock_tick), dummy1_tick)
        self.assertEqual(str(readDummy2.stock_name), dummy2_tick)
        self.assertEqual(str(readDummy2.stock_tick), dummy2_tick)

    def test_createStockItemYahooInfo(self):
        import pickle, os
        import copy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        #  /Users/yanghojun/Library/Mobile Documents/com~apple~CloudDocs/Code_mac/vscode/app_StockManager/django_kakaoChatbot/appStockInfo
        mainWrapper = MainWrapper()

        with open(
                os.path.join(
                    root,
                    'testMockData', 'stockList.p'
                ), 'rb'
        ) as f:
            mainWrapper.stockList = copy.deepcopy(pickle.load(f))

        with open(
                os.path.join(
                    root,
                    'testMockData', 'stockInfo.p'
                ), 'rb'
        ) as f:
            mainWrapper.stockInfo = copy.deepcopy(pickle.load(f))


        # Test info types
        count = 0
        for ticker in mainWrapper.stockInfo.infoYahooKOSPI:
            count += 1
            tmpData = mainWrapper.stockInfo.infoYahooKOSPI[ticker]
            print(f'ticker : {ticker}')
            print(f'tmpData.info["sector"] : {tmpData.info["sector"]}')
            print(f'tmpData.info["industry"] : {tmpData.info["industry"]}')
            if count >= 10:
                break
