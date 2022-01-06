import xgboost
import matplotlib.pyplot as plt
from sklearn.metrics import explained_variance_score

import logging
logger = logging.getLogger('appStockPrediction')

class Builder:

    def build(self, model_type, X_train, y_train, X_test, y_test, PX):

        assert model_type in ["XGBoost", "LSTM", "Dense"]

        if model_type == "XGBoost":
            return XGBoost.predict(X_train, y_train, X_test, y_test, PX)


class XGBoost:

    xgb_model = None

    @classmethod
    def predict(cls, X_train, y_train, X_test, y_test, PX):
        XGBoost.xgb_model = xgboost.XGBRegressor(n_estimators=500,
                                         reg_alpha=1,
                                         reg_lambda=1,
                                         subsample=0.75,
                                         learning_rate=0.3,
                                         gamma=0,
                                         colsample_bytree=1,
                                         max_depth=30,
                                         eval_metric="mape")

        # Train Model
        XGBoost.xgb_model.fit(X_train, y_train)

        # Plot importance
        # UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
        # terminating with uncaught exception of type NSException
        #xgboost.plot_importance(xgb_model)

        # Prediction for test
        test_predictions = XGBoost.xgb_model.predict(X_test)
        # Scores
        # 1)
        test_score = explained_variance_score(test_predictions, y_test)
        logger.info(f"MainWrapperKR - createPrediction; Prediction score test : {test_score}")
        # 2)
        train_score = XGBoost.xgb_model.score(X_train, y_train)
        logger.info(f"MainWrapperKR - createPrediction; Prediction score train : {train_score}")
        # 3)
        mpe = myMPE(test_predictions, y_test.to_numpy())
        logger.info(f"MainWrapperKR - createPrediction; Prediction score train/mpe : {mpe}")

        # Prediction for real
        real_predictions = XGBoost.xgb_model.predict(PX)

        return real_predictions



def myMPE( y_pred, y_true):
    return np.mean((y_true - y_pred) / y_true) * 100
