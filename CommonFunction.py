import ConfigFile as CONF


def retryOnFail(function):
    """
    retry running function if expexted results are not achieved
    """
    for _ in range(max(CONF.TOTAL_RETRY_FOR_FETCH_FAIL-1, 1)):
        try:
            return function()
        except:pass

    return function()