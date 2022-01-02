from appStockInfo.job.interface.KR.Wrapper import (
	MainWrapperKR
)
from appStockPrediction.job.interface.KR.ServiceStockPrediction import (
	MainWrapperKR as MWK_Prediction
)
import logging
logger = logging.getLogger('my')

def serviceKRStocks():
	"""Update KR stock info"""
	logger.info("serviceKRStocks - called from apscheduler")

	mainKRWrapper = MainWrapperKR()
	mainKRWrapper.doAction()


	mainKRWrapper_prediction = MWK_Prediction()
	mainKRWrapper_prediction.doAction()


def serviceUSStocks():
	"""Update US stock info"""
	logger.info("serviceUSStocks - called from apscheduler")
	pass