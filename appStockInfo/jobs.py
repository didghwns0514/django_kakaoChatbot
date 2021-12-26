from appStockInfo.job.interface.KR.Service import (
	MainWrapperKR
)
import logging
logger = logging.getLogger('my')

def serviceKRStocks():
	"""Update KR stock info"""
	logger.info("serviceKRStocks - called from apscheduler")

	mainKRWrapper = MainWrapperKR()
	mainKRWrapper.doAction()


def serviceUSStocks():
	"""Update US stock info"""
	logger.info("serviceUSStocks - called from apscheduler")
	pass