import xgboost
import numpy as np
import os
from pathlib import Path
#import matplotlib.pyplot as plt
from sklearn.metrics import (
    explained_variance_score,
    mean_squared_error,
    mean_absolute_error
)

import logging
logger = logging.getLogger('appStockPrediction')

class Builder:

    @classmethod
    def build(cls, model_type, X_train, y_train, X_test, y_test, PX):

        assert model_type in ["XGBoost", "LSTM", "Dense"]

        if model_type == "XGBoost":
            return XGBoost.predict(X_train, y_train, X_test, y_test, PX)

        elif model_type == "LSTM":
            pass

        elif model_type == "Dense":
            pass


class XGBoost:

    xgb_model = None

    @classmethod
    def predict(cls, X_train, y_train, X_test, y_test, PX):
        # XGBoost.xgb_model = xgboost.XGBRegressor(n_estimators=500,
        #                                  reg_alpha=1,
        #                                  reg_lambda=1,
        #                                  subsample=0.75,
        #                                  learning_rate=0.3,
        #                                  gamma=0,
        #                                  colsample_bytree=1,
        #                                  max_depth=30,
        #                                  eval_metric="mape")
        XGBoost.xgb_model = xgboost.XGBRegressor(
                                         seed=100,
                                         n_estimators=500,
                                         reg_alpha=1,
                                         reg_lambda=1,
                                         subsample=1,
                                         learning_rate=0.1,
                                         min_child_weight=1,
                                         gamma=0,
                                         colsample_bytree=1,
                                         colsample_bylevel=1,
                                         max_depth=30,
                                         )

        # Train Model
        XGBoost.xgb_model.fit(X_train, y_train)

        # Prediction for test
        test_predictions = XGBoost.xgb_model.predict(X_test)


        # Scores
        # 1)
        train_score = XGBoost.xgb_model.score(X_train, y_train)
        logger.info(f"MainWrapperKR - createPrediction; Prediction score train : {train_score}")
        # 2)
        test_score = explained_variance_score(test_predictions, y_test)
        logger.info(f"MainWrapperKR - createPrediction; Prediction score test - evs : {test_score}")
        # 3)
        # mpe = myMPE(test_predictions, y_test.to_numpy())
        # logger.info(f"MainWrapperKR - createPrediction; Prediction score train/mpe : {mpe}")
        # 4)
        rmse_score = mean_squared_error(test_predictions, y_test) **(0.5)
        logger.info(f"MainWrapperKR - createPrediction; Prediction score test - rmse: {rmse_score}")
        # 5)
        mae_score = mean_absolute_error(test_predictions, y_test)
        logger.info(f"MainWrapperKR - createPrediction; Prediction score test - mae: {mae_score}")

        # Prediction for real
        real_predictions = XGBoost.xgb_model.predict(PX)

        return real_predictions

    @classmethod
    def plot_importance(cls):
        # Plot importance
        # UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
        # terminating with uncaught exception of type NSException

        try:
            root = Path(__file__).resolve().parent.parent.parent.parent
            path = os.path.join(
                root,
                'testFolders',
                'result_XGBoost', 'xgboost_result.png'
            )
            result_image = xgboost.plot_importance(XGBoost.xgb_model)
            result_image.figure.tight_layout()
            result_image.figure.savefig(path)
        except:pass

def myMPE( y_pred, y_true):
    return np.mean((y_true - y_pred) / y_true) * 100
