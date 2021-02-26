"""
	For class setup
"""

class StockData(object):
	"""class for containing parsed data"""

	INDEX_STR = ['N', '종목명', '현재가', '전일비', '등락률', '액면가', '시가총액', '상장주식수', '외국인비율', '거래량', 'PER', 'ROE']

	def __init__(self, pIndex, pValue, source):
		"""

		:param pIndex: index (컬럼 이름)
		:param pValue: value parsed as a list
		:param source: 코스피 / 코스닥 utf-8
		"""

		self._pIndex = pIndex[:-1]
		self._pValue = [ filtered.replace('%','').replace(',','') for filtered in pValue ]

		# private attributes
		self.source = source
		self.num = None
		self.name = None
		self.priceNow = None
		self.priceCompared = None
		self.priceRatio = None
		self.priceStraight = None
		self.totalStockSum = None
		self.totalStockNum = None
		self.totalForeignRatio = None
		self.tradeSum = None
		self.PER = None
		self.ROE = None

		self.__alloc_parsed()

	def __alloc_parsed(self):

		arbitary_index = len(self._pValue) - (len(StockData.INDEX_STR)-2) if len(self._pValue) > 12 else 2

		self.num = str(self._pValue[0])
		self.name = str(' '.join(self._pValue[1:arbitary_index]))
		self.priceNow = float(self._pValue[arbitary_index].replace(',',''))

		self.priceRatio = float(self._pValue[arbitary_index+2].replace('+','').replace('%','')) \
			if  '+' in self._pValue[arbitary_index+2] \
				else - float(self._pValue[arbitary_index+2].replace('-','').replace('%','')) \
				if '-' in self._pValue[arbitary_index+2] else float(self._pValue[arbitary_index+2].replace('%',''))

		self.priceCompared = - float(self._pValue[arbitary_index+1]) if self.priceRatio < 0\
			else float(self._pValue[arbitary_index+1]) if self.priceRatio > 0 else float(self._pValue[arbitary_index+1])

		self.priceStraight = float(self._pValue[arbitary_index+3])
		self.totalStockSum = int(self._pValue[arbitary_index+4])
		self.totalStockNum = int(self._pValue[arbitary_index+5])
		self.totalForeignRatio = float(self._pValue[arbitary_index+6])
		self.tradeSum = int(self._pValue[arbitary_index+7])
		self.PER = float(self._pValue[arbitary_index+8]) if 'N/A' not in self._pValue[arbitary_index+8] else float(0)
		self.ROE = float(self._pValue[arbitary_index+9]) if 'N/A' not in self._pValue[arbitary_index+9] else float(0)


