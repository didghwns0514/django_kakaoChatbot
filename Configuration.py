"""
	For class setup
"""
from bs4 import BeautifulSoup
import lxml
import re
from datetime import datetime

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

	def toDict(self):
		"""to dump result as dictionary"""
		rnt_dict = {}
		rnt_dict[self.name] = {}

		rnt_dict[self.name]['source'] = self.source
		rnt_dict[self.name]['num'] = self.num
		rnt_dict[self.name]['name'] = self.name
		rnt_dict[self.name]['priceNow'] = self.priceNow
		rnt_dict[self.name]['priceCompared'] = self.priceCompared
		rnt_dict[self.name]['priceRatio'] = self.priceRatio
		rnt_dict[self.name]['priceStraight'] = self.priceStraight
		rnt_dict[self.name]['totalStockSum'] = self.totalStockSum
		rnt_dict[self.name]['totalStockNum'] = self.totalStockNum
		rnt_dict[self.name]['totalForeignRatio'] = self.totalForeignRatio
		rnt_dict[self.name]['tradeSum'] = self.tradeSum
		rnt_dict[self.name]['PER'] = self.PER
		rnt_dict[self.name]['ROE'] = self.ROE

		return rnt_dict



class NewsData_Naver:


	def __init__(self, pgSource, url, date_len):
		"""
		the result of the page
		:param pgSource: page source as text
		:param url: url of the source
		:param date: date length to archive
		"""
		self.pg_source = pgSource
		self.url = url
		print(f'self.url : {self.url}')
		self.article_date = None
		self.title = None
		self.date_len = date_len

		self.__alloc_parsed()

	def _clean_text(self, text2clean):
		cleaned_text = re.sub('[a-zA-Z]', '', text2clean)
		cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', cleaned_text)

		return cleaned_text.strip()


	def __alloc_parsed(self):

		tmp_bs4 = BeautifulSoup(self.pg_source, 'lxml', from_encoding='utf-8')

		# @ get title
		tmp_title = tmp_bs4.find("div", attrs={"class": "article_info"}).find('h3')
		self.title = self._clean_text(tmp_title.text)

		# @ get date
		tmp_date = tmp_bs4.find("span", attrs={"class": "article_date"})
		self.article_date = datetime.strptime(self._clean_text(tmp_date.text),
											  '%Y%m%d %H%M')

		# @ get content
		tmp_content = tmp_bs4.find("div", attrs={'class': 'articleCont', 'id':'content'})
		# cleaned_text = re.sub('[a-zA-Z]', '', text)
		# cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', cleaned_text)
		print(tmp_content.text)


	def _keep_data(self):
		"""True if keep, False if needs deletion"""
		return True