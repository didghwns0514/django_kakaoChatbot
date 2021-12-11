import unittest

from django.test import TestCase
from appStockInfo.job.interface.KR.Wrapper import (
    GetStockInfo, GetStockList, MainWrapper
)
from appStockInfo.job import (
    KRStock, USStock
)
from appStockInfo.models import (
    StockTick,
    StockItemList,
    StockItem
)
from appStockInfo.scheduler import taskStockUS, taskStockKR

class CreateKRStocks(TestCase):
    def test_mockStockTick(self):
        import pickle, os
        import copy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        print(f'root : {root}')
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
