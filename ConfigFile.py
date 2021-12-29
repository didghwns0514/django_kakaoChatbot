from datetime import datetime

# For fetching Data
TOTAL_REQUEST_DATE_LENGTH = 10
TOTAL_RETRY_FOR_FETCH_FAIL = 10
SLEEP_SECONDS_BETWEEN_RQ = 1.4

# For keeping old records
MAX_DAYS_KEEP_OLD_STOCKITEMS = 30


# Dataframe columns
DATAFRAME_COLUMN_NAMES = [
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