from datetime import datetime

# For fetching Data
TOTAL_REQUEST_DATE_LENGTH = 7
TOTAL_RETRY_FOR_FETCH_FAIL = 12
SLEEP_SECONDS_BETWEEN_RQ = 1.5

# For keeping old records
MAX_DAYS_KEEP_OLD_STOCKITEMS = 30

# Stock Time hour in KTZ
MARKET_TOTAL_FINISH_HOUR = 17

# Total Stock Nums Normalizer value
STOCK_NUM_NORMALIZER = 10**7

# Dataframe columns
DATAFRAME_COLUMN_NAMES = [
        "section_integer",
        "total_sum",
        "time_elapsed",
        "open",
        "high",
        "low",
        "close",
        "gap",
        "volume",
        "div",
        "per",
        "pbr",
        "market_name",
        "roe",
        "answer",
        "tick"
]


MARKET_NUMBER = {
        "Dummy" : 0,
        "KOSPI" : 1,
        "KOSDAQ" : 2
}

## Moeny
KR_BOTTOMLINE = 5000



# KRX configs
KRX__GEN_OPT_URL = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
KRX__GEN_OPT_DATA_KOSPI = {
        'mktId': 'STK',
        'trdDd': datetime.today().strftime("%Y%m%d"),
        'money': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'
    }
KRX__GEN_OPT_DATA_KOSDAQ  = {
        'mktId': 'KSQ',  # 코스닥 입력
        'trdDd': datetime.today().strftime("%Y%m%d"),
        'money': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'
    }