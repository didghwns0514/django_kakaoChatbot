import ConfigFile as CONF

from pytimekr import pytimekr
import datetime, pandas as pd

import logging
logger = logging.getLogger('my')


def getMarketNumber(marketString:str):
    """
    return market number from market name string
    """
    if marketString in CONF.MARKET_NUMBER:
        return CONF.MARKET_NUMBER[str(marketString)]
    else:
        return CONF.MARKET_NUMBER["Dummy"]


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
        counter >= 100:
        callDateFiltered += datetime.timedelta(days=1)
        counter += 1

    return callDateFiltered


def getStartFetchingDate(callEndDate:datetime.datetime):

    for _ in range(CONF.TOTAL_RETRY_FOR_FETCH_FAIL):
        kr_holidays = pytimekr.holidays()
        if kr_holidays: break
    else:
        logger.critical('getStartFetchingDate; Date generation failed')

    if not CONF.MARKET_TOTAL_FINISH_HOUR <= callEndDate.hour < 24:
        callEndDate -= datetime.timedelta(days=1) # get more data worth of 1 day

    callDateFiltered = datetime.datetime(
        callEndDate.year, callEndDate.month, callEndDate.day
    )

    # 0, 1, 2, 3, 4, 5, 6
    # 월, 화, 수, 목, 금, 토, 일
    counter = 0
    counterRequiredDates = 0
    while counter < 100:
        if (callDateFiltered.weekday() in [5, 6]) or callDateFiltered in kr_holidays:
            pass
        else: counterRequiredDates += 1
        callDateFiltered -= datetime.timedelta(days=1)

        if counterRequiredDates >= CONF.TOTAL_REQUEST_DATE_LENGTH:
            break

        counter += 1

    return callDateFiltered


def generateEmptyDataframe(switch:str="Main"):

    assert(switch in ["Main", "Prediction", "Window"])

    if switch == "Main":
        globalDataframeMain = pd.DataFrame(
            columns=CONF.DATAFRAME_COLUMN_NAMES
        )
        return globalDataframeMain
    elif switch == "Window":
        globalDataframeWindow = pd.DataFrame(
            columns=CONF.DATAFRAME_COLUMN_NAMES
        )
        return globalDataframeWindow
    elif switch == "Prediction":
        globalDataframePredictions = pd.DataFrame(
            columns=CONF.DATAFRAME_COLUMN_NAMES[:len(CONF.DATAFRAME_COLUMN_NAMES) - 2]  # "answer" / "tick" removed
        )
        return globalDataframePredictions
    else:
        raise Exception("Not configured Empty Datafame")