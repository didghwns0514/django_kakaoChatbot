import datetime

from django.test import TestCase
from sklearn.preprocessing import MinMaxScaler

import CommonFunction as CF
from appStockPrediction.job.interface.KR.ServiceStockPrediction import (
    MainWrapperKR
)
from appStockPrediction.job.interface.predictionModels.builder import (
    XGBoost
)

class PredictionXGBoost(TestCase):

    reset_sequences = True

    def test_checkDataframe(self):
        import pickle, os
        import copy
        from pathlib import Path
        import pandas as pd

        root = Path(__file__).resolve().parent.parent
        print(f'root : {root}')

        with open(
                os.path.join(
                    root,
                    'testMockData', 'tmpMainDF.p'
                ), 'rb'
        ) as f:
            tmpMainDF = copy.deepcopy(pickle.load(f))

        with open(
                os.path.join(
                    root,
                    'testMockData', 'tmpPredDF.p'
                ), 'rb'
        ) as f:
            tmpPredDF = copy.deepcopy(pickle.load(f))

        print(f'tmpPredDF.head(10) : \n{tmpPredDF.head(10)}')
        print(f'tmpMainDF.head(10) : \n{tmpMainDF.head(10)}')
        print(f'len(tmpPredDF) : \n{len(tmpPredDF)}')
        print(f'len(tmpMainDF) : \n{len(tmpMainDF)}')


    def test_predictXGBoost(self):
        import pickle, os
        import copy
        from pathlib import Path
        import pandas as pd

        root = Path(__file__).resolve().parent.parent
        print(f'root : {root}')

        with open(
                os.path.join(
                    root,
                    'testMockData', 'tmpMainDF.p'
                ), 'rb'
        ) as f:
            tmpMainDF = copy.deepcopy(pickle.load(f))

        with open(
                os.path.join(
                    root,
                    'testMockData', 'tmpPredDF.p'
                ), 'rb'
        ) as f:
            tmpPredDF = copy.deepcopy(pickle.load(f))

        print(f'tmpPredDF.head(10) : \n{tmpPredDF.head(10)}')
        print(f'tmpMainDF.head(10) : \n{tmpMainDF.head(10)}')

        mainWrapper = MainWrapperKR()
        dataframeWindowDummy = CF.generateEmptyDataframe("Window")
        datetimTest = datetime.datetime(2022, 1, 6, 10)

        # Run analysis
        predictionDF, _ = mainWrapper.createPrediction(
            datetimTest, tmpMainDF, tmpPredDF, dataframeWindowDummy
        )

        # check information
        predictionDF.info()

        sortedDF = predictionDF.sort_values(by=["prediction"], ascending=False)
        print(f'sortedDF.head(10) : \n{sortedDF.head(10)}')

        i=0
        for idx, row in sortedDF.iterrows():
            i += 1
            if i > 8 : break
            tmpTick = row['tick']
            tmpPrediction = row['prediction']
            tmpClose = row['close']
            tmpOpen = row['open']
            tmpGap = row['gap']

            print(f'tmpTick : {tmpTick}')
            print(f'tmpPrediction : {tmpPrediction}')
            print(f'tmpClose : {tmpClose}')
            print(f'tmpOpen : {tmpOpen}')
            print(f'tmpGap : {tmpGap}')
            print(f'-'*20)

        # do Plot
        XGBoost.plot_importance()


        # min max scale on rows
        # row_minMaxScaler = MinMaxScaler()
        # new = pd.DataFrame(row_minMaxScaler.fit_transform(tmpMainDF[["open", 'close', 'low', 'high']].T).T, columns=["open", 'close', 'low', 'high'])
        # print(f'new.head(10) : \n{new.head(10)}')