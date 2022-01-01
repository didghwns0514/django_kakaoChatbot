import ConfigFile as CONF

from pytimekr import pytimekr
import datetime, pandas as pd

import logging
logger = logging.getLogger('my')

def retryOnFail(function):
    """
    retry running function if expexted results are not achieved
    """
    for _ in range(max(CONF.TOTAL_RETRY_FOR_FETCH_FAIL-1, 1)):
        try:
            return function()
        except:pass

    return function()


def getNextPredictionDate(callDate:datetime.datetime):
    # https://velog.io/@vanang7/Python으로-공휴일-리스트를-만들자
    for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
        kr_holidays = pytimekr.holidays()
        if kr_holidays: break
    else: logger.critical('getNextPredictionDate; Date generation failed')

    if CONF.MARKET_TOTAL_FINISH_HOUR <= callDate.hour < 24:
        callDate += datetime.timedelta(days=1)

    callDateFiltered = datetime.datetime(
        callDate.year, callDate.month, callDate.day
    )

    # 0, 1, 2, 3, 4, 5, 6
    # 월, 화, 수, 목, 금, 토, 일
    counter = 0
    while ( callDateFiltered.weekday() in [5, 6]) or callDateFiltered in kr_holidays or \
        counter >= 7:
        callDateFiltered += datetime.timedelta(days=1)
        counter += 1

    return callDateFiltered


def generateEmptyDataframe(switch:str="Main"):

    assert(switch in ["Main", "Prediction"])

    if switch == "Main":
        globalDataframeMain = pd.DataFrame(
            columns=CONF.DATAFRAME_COLUMN_NAMES
        )
        return globalDataframeMain
    elif switch == "Prediction":
        globalDataframePredictions = pd.DataFrame(
            columns=CONF.DATAFRAME_COLUMN_NAMES[:len(CONF.DATAFRAME_COLUMN_NAMES) - 2]  # "answer" / "tick" removed
        )
        return globalDataframePredictions
    else:
        raise Exception("Not configured Empty Datafame")