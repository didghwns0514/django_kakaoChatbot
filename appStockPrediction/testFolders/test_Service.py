import unittest
from django.test import TestCase
from django.db.models import (
    Q, F
)
from appStockInfo.models import (
    StockItem,
    StockTick,
    StockSection,
    StockItemListSection,
    StockItemListName,

)
from appStockPrediction.job.interface.KR.ServiceStockPrediction import (
    MainWrapperKR
)
import ConfigFile as CONF
import CommonFunction as CF

from appStockInfo.job.interface.KR.Wrapper import MainWrapperKR as MKR

import datetime
import pandas as pd


class CommonFunction(TestCase):

    def test_getNextPredictionDate(self):
        stampDate = datetime.datetime(2021,12,11,19)
        print(f'start date : {stampDate}')
        newDate = CF.getNextPredictionDate(stampDate)
        print(f'end date : {newDate}')


class MainWrapper(TestCase):


    def test_createPrediction(self):

        # R
        self.base_samsung()

        tickSamsung = "005930"
        sectionSamsung = "전기전자"
        callDate = datetime.date(2021,12,27)

        column_names = [
            "section_integer",
            "total_sum",
            "time_elapsed",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "div",
            "per",
            "pbr",
            "roe",
            "answer"
        ]
        globalDataframeMain = pd.DataFrame(
            columns=column_names
        )
        globalDataframePredictions = pd.DataFrame(
            columns=column_names[:len(column_names)-1]
        )

        # cached stockitems
        all_Stockitems = StockItem.objects.all()
        print(f'len(all_Stockitems) : {len(all_Stockitems)}')

        # work with information provided information
        exist_stocktick = StockTick.objects.filter(
            Q(stock_tick=tickSamsung)
        )
        self.assertEqual(
            exist_stocktick.exists(), True
        )
        exist_stockitem = StockItem.objects.filter(
            Q(stock_name__stock_tick__stock_tick=tickSamsung)
        )
        self.assertEqual(
            exist_stockitem.exists(), True
        )

        # test
        mainWrapperKR = MainWrapperKR()
        tmpMain, tmpPrediction = mainWrapperKR.createDataframe(tickSamsung, all_Stockitems=all_Stockitems,
                                                               callDate=callDate)

        print(f'tmpMain.head(3) : {tmpMain.head(3)}')
        print(f'tmpPrediction.head(1) : {tmpPrediction.head(1)}')


        # Test
        # 0) Need checking on mutable
        # 1) more than 1 days of data
        self.assertGreater(
            len(tmpMain), 1
        )
        self.assertEqual(
            len(tmpPrediction), 1
        )

    def base_samsung(self):
        """
        for base needed for appStockPrediction
        """
        import pickle, os
        import copy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent.parent
        #  /Users/yanghojun/Library/Mobile Documents/com~apple~CloudDocs/Code_mac/vscode/app_StockManager/django_kakaoChatbot/appStockInfo
        self.mainWrapper = MKR()

        with open(
                os.path.join(
                    root,
                    'appStockInfo',
                    'testMockData', 'stockList.p'
                ), 'rb'
        ) as f:
            self.mainWrapper.stockList = copy.deepcopy(pickle.load(f))

        with open(
                os.path.join(
                    root,
                    'appStockInfo',
                    'testMockData', 'stockInfo.p'
                ), 'rb'
        ) as f:
            self.mainWrapper.stockInfo = copy.deepcopy(pickle.load(f))

        tickSamsung = "005930"
        sectionSamsung = "전기전자"

        # Test
        # Required
        self.mainWrapper.createStockTick(
            [tickSamsung], "KOSPI"
        )

        self.mainWrapper.createStockItemListName(
            [tickSamsung], "KOSPI"
        )

        self.mainWrapper.createStockSection()
        self.mainWrapper.createStockItemListSection()

        # run tests
        self.mainWrapper.createStockItem()
