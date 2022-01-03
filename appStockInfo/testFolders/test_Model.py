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
    StockLastUpdateTime,
    StockItemListSection
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


    def test_createStockItemListNameUpdateCheck(self):
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

        # Requirements
        # Test Model
        ## Add dummys in KOSPI
        dummy1_tick = "000000"  # Added from StockTick
        dummy1_name = "000000"
        dummy2_tick = "000001"  # Not included in StockTick
        dummy2_name = "테스트1"
        nameSpace = {
            dummy1_tick: dummy1_name,
            dummy2_tick: dummy2_name
        }

        # First Creation
        tmp_StockList = copy.deepcopy(mainWrapper.stockList.KOSPI)

        # Update records in Main Memory
        tmp_StockList.extend([dummy1_tick, dummy2_tick])
        mainWrapper.stockList.tickerToName.update(nameSpace)

        mainWrapper.createStockItemListName(
            tmp_StockList
        )

        # check
        readDummy1 = StockItemListName.objects.get(stock_tick=dummy1_tick)
        readDummy2 = StockItemListName.objects.get(stock_tick=dummy2_tick)

        # assertions
        self.assertEqual(str(readDummy1.stock_name), dummy1_tick)
        self.assertEqual(str(readDummy1.stock_tick), dummy1_tick)
        self.assertEqual(str(readDummy2.stock_name), dummy2_name)
        self.assertEqual(str(readDummy2.stock_tick), dummy2_tick)


        # Second Update
        # tmp_StockList = copy.deepcopy(mainWrapper.stockList.KOSPI)
        dummy1_name = "업데이트1"
        nameSpace[dummy1_tick] = dummy1_name
        mainWrapper.stockList.tickerToName.update(nameSpace)

        # Update
        mainWrapper.createStockItemListName(
            tmp_StockList
        )

        # check
        readDummy1 = StockItemListName.objects.get(stock_tick=dummy1_tick)
        readDummy2 = StockItemListName.objects.get(stock_tick=dummy2_tick)

        # assertions
        self.assertEqual(str(readDummy1.stock_name), dummy1_name)
        self.assertEqual(str(readDummy1.stock_tick), dummy1_tick)
        self.assertEqual(str(readDummy2.stock_name), dummy2_name)
        self.assertEqual(str(readDummy2.stock_tick), dummy2_tick)


    def test_createStockItemListName(self):
        import pickle, os
        import copy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
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


    def test_createStockItemUpdate(self):

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

        # Check
        tmpInfoTickerKOSPI = mainWrapper.stockInfo.infoTickerKOSPI.keys()
        tmpInfoTickerKOSDAQ = mainWrapper.stockInfo.infoTickerKOSDAQ.keys()
        tmpInfoBasicKOSPI = mainWrapper.stockInfo.infoBasicKOSPI.keys()
        tmpInfoBasicKOSDAQ = mainWrapper.stockInfo.infoBasicKOSDAQ.keys()
        # List
        tmpTickerKOSPI = mainWrapper.stockList.KOSPI
        tmpTickerKOSDAQ = mainWrapper.stockList.KOSDAQ

        # Check - print
        print(f'tmpInfoTickerKOSPI : {len(tmpInfoTickerKOSPI)}')
        print(f'tmpInfoTickerKOSDAQ : {len(tmpInfoTickerKOSDAQ)}')
        print(f'tmpInfoBasicKOSPI : {len(tmpInfoBasicKOSPI)}')
        print(f'tmpInfoBasicKOSDAQ : {len(tmpInfoBasicKOSDAQ)}')
        print(f'tmpTickerKOSPI : {len(tmpTickerKOSPI)}')
        print(f'tmpTickerKOSDAQ : {len(tmpTickerKOSDAQ)}')
        # Check - partial
        CheckTick ="950210"
        print(f'in tmpInfoTickerKOSPI ? : {CheckTick in tmpInfoTickerKOSPI }')
        print(f'in tmpInfoTickerKOSDAQ ? : {CheckTick in tmpInfoTickerKOSDAQ }')
        print(f'in tmpInfoBasicKOSPI ? : {CheckTick in tmpInfoBasicKOSPI }')
        print(f'in tmpInfoBasicKOSDAQ ? : {CheckTick in tmpInfoBasicKOSDAQ }')
        print(f'in tmpTickerKOSPI ? : {CheckTick in tmpTickerKOSPI }')
        print(f'in tmpTickerKOSDAQ ? : {CheckTick in tmpTickerKOSDAQ }')


        # Test
        # Required
        #mainWrapper.getLoggerForAllInfos()

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
        mainWrapper.createStockItemListSection()

        # run tests
        mainWrapper.createStockItem()

        # check second run
        mainWrapper.createStockItem()


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

        # Check
        tmpInfoTickerKOSPI = mainWrapper.stockInfo.infoTickerKOSPI.keys()
        tmpInfoTickerKOSDAQ = mainWrapper.stockInfo.infoTickerKOSDAQ.keys()
        tmpInfoBasicKOSPI = mainWrapper.stockInfo.infoBasicKOSPI.keys()
        tmpInfoBasicKOSDAQ = mainWrapper.stockInfo.infoBasicKOSDAQ.keys()
        # List
        tmpTickerKOSPI = mainWrapper.stockList.KOSPI
        tmpTickerKOSDAQ = mainWrapper.stockList.KOSDAQ

        # Check - print
        print(f'tmpInfoTickerKOSPI : {len(tmpInfoTickerKOSPI)}')
        print(f'tmpInfoTickerKOSDAQ : {len(tmpInfoTickerKOSDAQ)}')
        print(f'tmpInfoBasicKOSPI : {len(tmpInfoBasicKOSPI)}')
        print(f'tmpInfoBasicKOSDAQ : {len(tmpInfoBasicKOSDAQ)}')
        print(f'tmpTickerKOSPI : {len(tmpTickerKOSPI)}')
        print(f'tmpTickerKOSDAQ : {len(tmpTickerKOSDAQ)}')
        # Check - partial
        CheckTick ="950210"
        print(f'in tmpInfoTickerKOSPI ? : {CheckTick in tmpInfoTickerKOSPI }')
        print(f'in tmpInfoTickerKOSDAQ ? : {CheckTick in tmpInfoTickerKOSDAQ }')
        print(f'in tmpInfoBasicKOSPI ? : {CheckTick in tmpInfoBasicKOSPI }')
        print(f'in tmpInfoBasicKOSDAQ ? : {CheckTick in tmpInfoBasicKOSDAQ }')
        print(f'in tmpTickerKOSPI ? : {CheckTick in tmpTickerKOSPI }')
        print(f'in tmpTickerKOSDAQ ? : {CheckTick in tmpTickerKOSDAQ }')


        # Test
        # Required
        #mainWrapper.getLoggerForAllInfos()

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
        mainWrapper.createStockItemListSection()

        # run tests
        mainWrapper.createStockItem()

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
        self.assertEqual(
            StockItemListSection.objects.filter(
                stock_tick__stock_tick=tickSamsung
            ).exists(), True
        )

        # Check for finance info
        tmpFinanceInfo = mainWrapper.stockInfo.infoFinanceData
        tmpSelectedDF_code = tmpFinanceInfo.loc[tmpFinanceInfo['종목코드'] == tickSamsung]

        self.assertEqual(
            tmpSelectedDF_code.empty, False
        )
        # Check StockItems existance
        tmpQuery_StockTick = StockTick.objects.all()
        print(f'len(tmpQuery_StockTick) : {len(tmpQuery_StockTick)}')

        tmpQuery_StockItemListName = StockItemListName.objects.all()
        print(f'len(tmpQuery_StockItemListName) : {len(tmpQuery_StockItemListName)}')

        tmpQuery_StockSection = StockSection.objects.all()
        print(f'len(tmpQuery_StockSection) : {len(tmpQuery_StockSection)}')

        tmpQuery_StockItemListSection = StockItemListSection.objects.all()
        print(f'len(tmpQuery_StockItemListSection) : {len(tmpQuery_StockItemListSection)}')

        tmpQuery_StockItem = StockItem.objects.all()
        print(f'len(tmpQuery_StockItem) : {len(tmpQuery_StockItem)}')

        # Stock Item exist check
        self.assertEquals(
            StockItem.objects.filter(
                stock_name__stock_tick__stock_tick=tickSamsung
            ).exists(), True
        )

        # Stock Item delete check - Samsung
        tmpQuery_StockItemSamsung = StockItem.objects.filter(
            stock_name__stock_tick__stock_tick=tickSamsung
        )
        if tmpQuery_StockItemSamsung.exists():
            tmpQuery_StockItemsFilter = \
                tmpQuery_StockItem.filter(
                    stock_name__stock_tick__stock_tick=tickSamsung
                ).order_by('-reg_date')
            firstRecord = tmpQuery_StockItemsFilter.first()
            lastRecord = tmpQuery_StockItemsFilter.last()
            print(f'lastRecord, firstRecord : {lastRecord.reg_date}, {firstRecord.reg_date}')
            firstRecordDate = datetime.datetime(
                firstRecord.reg_date.year,
                firstRecord.reg_date.month,
                firstRecord.reg_date.day,
                hour=19
            )
            mainWrapper.deleteStockItem(firstRecordDate)

            # Requery
            tmpQuery_StockItem = StockItem.objects.filter(
                  Q(stock_name__stock_tick__stock_tick=tickSamsung) \
                & Q(reg_date__range=(lastRecord.reg_date, firstRecord.reg_date))
            )
            self.assertEqual(
                tmpQuery_StockItem.exists(), True
            )
        else: raise Exception("Wrong path")

    def test_updateStockLastUpdateTime(self):
        mainWrapper = MainWrapperKR()

        # Required
        tmpTodayDateStamp = datetime.datetime.now()
        mainWrapper.updateStockLastUpdateTime(tmpTodayDateStamp)

        self.assertEqual(
            StockLastUpdateTime.objects.filter(
                update_time=tmpTodayDateStamp
            ).exists(), True
        )