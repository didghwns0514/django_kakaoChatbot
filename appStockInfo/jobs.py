import datetime

from appStockInfo.job.interface.KR.Wrapper import (
    MainWrapperKR
)
from appStockPrediction.job.interface.KR.ServiceStockPrediction import (
    MainWrapperKR as MWK_Prediction
)
import ConfigFile as CONF

import logging

logger = logging.getLogger('my')


def serviceKRStocks():
    """Update KR stock info"""
    logger.info("serviceKRStocks - called from apscheduler")

    KRgenData()
    KRgenPrediction()


def KRgenData():
    mainKRWrapper = MainWrapperKR()
    mainKRWrapper.doAction()


def KRgenPrediction(
        calledDatetime=datetime.datetime.now(),
        krbottomline=CONF.KR_BOTTOMLINE,
        krvolumefilter=CONF.KR_TOP_VOLUME_FILTER
):
    mainKRWrapper_prediction = MWK_Prediction()
    mainKRWrapper_prediction.doAction(calledDatetime=calledDatetime,
                                      krbottomline=krbottomline,
                                      krvolumefilter=krvolumefilter)


def serviceUSStocks():
    """Update US stock info"""
    logger.info("serviceUSStocks - called from apscheduler")
    pass
