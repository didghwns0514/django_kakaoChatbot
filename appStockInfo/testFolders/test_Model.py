import datetime
import unittest

from django.test import TestCase
from django.db.models import Q, F
from appStockInfo.job.interface.KR.Wrapper import (
    GetStockInfo, GetStockList, MainWrapperKR
)

from appStockInfo.models import (
    StockTick,
    StockItemListName,
    StockItem,
    StockSection,
    StockLastUpdateTime
)
from appStockInfo.scheduler import taskStockUS, taskStockKR

class CreateKRStocks(TestCase):
    def test_createStockTick(self):
        import pickle, os
        import copy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        #print(f'root : {root}')
        mainWrapper = MainWrapperKR()

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
        mainWrapper = MainWrapperKR()

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


    @unittest.skip("Info finance checked - pass")
    def test_getFinanceData(self):
        import pickle, os
        import copy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        #  /Users/yanghojun/Library/Mobile Documents/com~apple~CloudDocs/Code_mac/vscode/app_StockManager/django_kakaoChatbot/appStockInfo
        mainWrapper = MainWrapperKR()

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
        infoFinance = mainWrapper.stockInfo.infoFinanceData
        print(f'len(infoFinance) : {len(infoFinance)}')
        print(f'infoFinance.head(10) : {infoFinance.head(10)}')



    def test_createStockSection(self):
        import pickle, os
        import copy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        #  /Users/yanghojun/Library/Mobile Documents/com~apple~CloudDocs/Code_mac/vscode/app_StockManager/django_kakaoChatbot/appStockInfo
        mainWrapper = MainWrapperKR()

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

        # Test
        mainWrapper.createStockSection()

        section1 = "서비스업"
        section2 = "기타금융"
        querySet = StockSection.objects.filter(
            Q(section_name=section1) | Q(section_name=section2)
        )
        self.assertEqual(querySet.exists(), True)
        self.assertEqual(querySet.exists(), True)

    @unittest.skip("checked working - pass")
    def test_getStockdata(self):
        import pickle, os
        import copy
        from pathlib import Path
        import pandas as pd

        root = Path(__file__).resolve().parent.parent
        #  /Users/yanghojun/Library/Mobile Documents/com~apple~CloudDocs/Code_mac/vscode/app_StockManager/django_kakaoChatbot/appStockInfo
        mainWrapper = MainWrapperKR()

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

        # Test
        tickSamsung = "005930"
        ## check infos
        print(f'KOSPI basic info samsung')
        print(f'mainWrapper.stockInfo.infoBasicKOSPI : {mainWrapper.stockInfo.infoBasicKOSPI[tickSamsung]}')

        print(f'KOSPI Ticker info samsung')
        print(f'mainWrapper.stockInfo.infoTickerKOSPI : {mainWrapper.stockInfo.infoTickerKOSPI[tickSamsung]}')

        concatDF = pd.concat(
            [
                mainWrapper.stockInfo.infoBasicKOSPI[tickSamsung],
                mainWrapper.stockInfo.infoTickerKOSPI[tickSamsung]
            ],
            axis=1
        )
        """
        > roe : (당기순이익)/(자본총액) = EPS/BPS
        > 
        """
        concatDF['ROE'] = concatDF['EPS']/concatDF['BPS'] * 100

        print(f'concatDF : {concatDF}')

        infoFinanceDF = mainWrapper.stockInfo.infoFinanceData
        selectedDF = infoFinanceDF.loc[infoFinanceDF['종목코드'] == tickSamsung]

        print(f'selectedDF : {selectedDF}')
        print(f'type(selectedDF) : {type(selectedDF)}')

        totalSum = int( selectedDF["시가총액"] )
        print(f'selectedDF : {totalSum}')
        print(f'type(selectedDF) : {type(totalSum)}')


        for idx, row in concatDF.iterrows():
            print(f'idx : {idx}')
            print(f'row : {row}')

    def test_createStockItem(self):

        import pickle, os
        import copy
        from pathlib import Path
        import pandas as pd

        root = Path(__file__).resolve().parent.parent
        #  /Users/yanghojun/Library/Mobile Documents/com~apple~CloudDocs/Code_mac/vscode/app_StockManager/django_kakaoChatbot/appStockInfo
        mainWrapper = MainWrapperKR()

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

        # Test
        # Required
        mainWrapper.createStockTick(
            mainWrapper.stockList.KOSPI, "KOSPI"
        )
        mainWrapper.createStockTick(
            mainWrapper.stockList.KOSDAQ, "KOSDAQ"
        )
        mainWrapper.createStockItemListName(
            mainWrapper.stockList.KOSPI, "KOSPI"
        )
        mainWrapper.createStockItemListName(
            mainWrapper.stockList.KOSDAQ, "KOSDAQ"
        )
        mainWrapper.createStockSection()

        # run tests
        mainWrapper.createStockItem(
            mainWrapper.stockList.KOSPI, "KOSPI"
        )
        mainWrapper.createStockItem(
            mainWrapper.stockList.KOSDAQ, "KOSDAQ"
        )

        tickSamsung = "005930"
        sectionSamsung = "전기전자"

        # Stock List exist check
        self.assertEqual(
            tickSamsung in mainWrapper.stockList.KOSPI, True
        )
        self.assertEqual(
            StockTick.objects.filter(
                stock_tick=tickSamsung
            ).exists(), True
        )
        self.assertEqual(
            StockItemListName.objects.filter(
                stock_tick__stock_tick=tickSamsung
            ).exists(), True
        )
        self.assertEqual(
            StockSection.objects.filter(
                section_name=sectionSamsung
            ).exists(), True
        )

        # Check for finance info
        tmpFinanceInfo = mainWrapper.stockInfo.infoFinanceData
        tmpSelectedDF_code = tmpFinanceInfo.loc[tmpFinanceInfo['종목코드'] == tickSamsung]

        self.assertEqual(
            tmpSelectedDF_code.empty, False
        )

        # Stock Item exist check
        self.assertEquals(
            StockItem.objects.filter(
                stock_name__stock_tick__stock_tick=tickSamsung
            ).exists(), True
        )

    def test_updateStockLastUpdateTime(self):
        mainWrapper = MainWrapperKR()

        # Required
        mainWrapper.updateStockLastUpdateTime()

        tmpTodayDateStamp = datetime.datetime.today()
        self.assertEqual(
            StockLastUpdateTime.objects.filter(
                update_time=tmpTodayDateStamp
            ).exists(), True
        )