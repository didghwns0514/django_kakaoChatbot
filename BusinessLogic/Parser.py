"""
	Parser

	to check how to use xpath
	>>> https://www.w3schools.com/xml/xpath_syntax.asp

"""

from selenium import webdriver
from bs4 import BeautifulSoup
from Configuration import *
import lxml
from pathlib import Path
import os
from datetime import datetime, timedelta



class Selenium:

	# @ setup args
	#location = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "static", "chromedriver")
	location = 'usr/src/app/static/chromedriver'
	options = webdriver.ChromeOptions()
	args = ['headless', 'window-size=1920x1080', 'disable-gpu',
			"user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"]
	for arg in args:
		options.add_argument(arg)

	# @ static var for holding result
	dResult = None

	# @ flags for successful jobs
	flags = {
		'stock_list':False,
		'news_list':False
	}

	# @ error counters
	errjobs_stocklist = 0
	errjobs_newscrawl = 0

	# @ parse methods for given modules
	parse_method = {'page' : '&page=',
					'date' : '&date=',
					'mk_page' : 'page=',
					'naver_date_page' : {'date':'&date=',
										 'page':'&page='}}

	# @ module description in dictionary
	parse_module = {
		'stock_list_kospi' : {
						'url':'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page=1',
						'alter':'page',
						'page' : None, # page number,
						'source' : '코스피',
						},
		'stock_list_kosdaq' : {
						'url' : 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=1&page=1',
						'alter':'page',
						'page' : None, # page number,
						'source' : '코스닥',
						},
		'news_list_naver' : {
						'url':'https://finance.naver.com/news/news_list.nhn?mode=LSS2D&section_id=101&section_id2=258&date=' + datetime.now().strftime("%Y%m%d") + '&page=1',
						'alter' : 'naver_date_page',
						'date': None,
						'activated' : True,
						'date_back' : int(3)
						},
		'news_list_mk' : {
						'url': 'https://www.mk.co.kr/news/stock/?page=1',
						'alter' : 'mk_page',
						'date': None,
						'activated' : True,
						'date_back' : int(3)
		}
	}

	# @ save results
	pResult = {
		'stock_list_kospi' : {},
		'stock_list_kosdaq' : {},
		'news_list' : {}
	}

	def __init__(self):
		# @ driver
		print(f'PATH!!!!: { Selenium.location }')

		# '../static/chromedriver'
		self.driver = webdriver.Chrome(Selenium.location, chrome_options=Selenium.options)
		self.driver.implicitly_wait(3)


	def __getDriver(self, url:str):
		"""load driver a url"""
		try:
			# print(f'SeleniumUpdater.driver : {SeleniumUpdater.driver}')
			# print(f'type(SeleniumUpdater.driver) : {type(SeleniumUpdater.driver)}')
			if self.driver.current_url != url:
				self.driver.get(url)
		except:
			pass


	def __findTagElement(self, module:str, methodString:str, targUrl:str=None):
		"""
		method to find tag elements
		:param methodString:
		:return:
		"""
		# @ init
		Selenium.dResult = None

		if targUrl == None: # set target from dictionary
			mode = Selenium.parse_module[module]
			self.__getDriver(mode['url'])
		else:
			self.__getDriver(targUrl)

		Selenium.dResult = self.driver.find_element_by_xpath(methodString)

		return Selenium.dResult


	def _crawl_stock_list(self, state='stock_list'):

		print(f'Selenium.errjobs_stocklist : {Selenium.errjobs_stocklist}')

		tmp_module_key = [ key_lv1 for key_lv1, val1 in zip(Selenium.parse_module.keys(), Selenium.parse_module.values())
						   if state in key_lv1]
		try:
			for module in tmp_module_key:

				tmp_alter = Selenium.parse_method[Selenium.parse_module[module]['alter']]
				assert isinstance(tmp_alter, str)
				# tmp_pgUrl_res = SeleniumUpdater.__findTagElement(module=module,
				# 										  methodString= '//td[@class="pgRR"]/a[@href]'
				# 										  )[0].get_attribute('href')
				tmp_pgUrl_res = self.__findTagElement(module=module,
														  methodString= '//td[@class="pgRR"]/a[@href]'
														  ).get_attribute('href')

				if tmp_pgUrl_res != None : # if the wanted result is parsed

					tmp_href, tmp_last_pg = tmp_pgUrl_res.split(tmp_alter)

					for pg_num in range(1, int(tmp_last_pg) + 1):
						tmp_url = tmp_href + tmp_alter + str(pg_num)

						tmp_targHead = self.__findTagElement(module=module,
																 methodString= \
										'//div[@id="contentarea"]' + \
										'/div[@class]' + \
										'/table[@class="type_2"]' + \
										'/thead/tr',
										 targUrl=tmp_url).find_elements_by_xpath('//th[@scope]')
						tmp_headList = [ obj.text for obj in tmp_targHead ]


						tmp_htmlSource = self.driver.page_source
						soup = BeautifulSoup(tmp_htmlSource, 'lxml')
						tmp_targVar = soup.find("table", attrs={"class": "type_2"}).find("tbody").find_all("tr")
						tmp_varList = []
						_ = [tmp_varList.append(obj.get_text().split()) for obj in tmp_targVar if len(obj.get_text()) > 1]

						# @ append container
						for var_list in tmp_varList:
							tmp_containerCls = StockData(tmp_headList, var_list, source=Selenium.parse_module[module]['source'])
							Selenium.pResult[module][tmp_containerCls.name] = tmp_containerCls

					# set the flag up
					Selenium.flags[module] = True

			# when done parsing
			rtn_all_dict = {}
			for module_key in Selenium.pResult:
				for stockName_key in Selenium.pResult[module_key]:
					tmp_cls = Selenium.pResult[module_key][stockName_key]
					rtn_all_dict.update(tmp_cls.toDict())

			return rtn_all_dict

		except Exception as e:
			print(f'error : {e}')
			traceback.print_exc()

			# error cnt up
			Selenium.errjobs_stocklist += 1

			try:
				self.driver.close()
				# reload
				self.driver = webdriver.Chrome('./static/chromedriver', chrome_options=Selenium.options)
				self.driver.implicitly_wait(3)
			except:
				pass


	def _craw_news(self, state='news_list'):
		"""crawl news"""
		print(f'Selenium.errjobs_newscrawl : {Selenium.errjobs_newscrawl}')

		tmp_module_key = [ key_lv1 for key_lv1, val1 in zip(Selenium.parse_module.keys(), Selenium.parse_module.values())
						   if state in key_lv1]

		try:
			for module in tmp_module_key:
				if module == 'news_list_naver':
					if Selenium.parse_module[module]['activated']:
						self.__crawl_news_naver(module)

				elif module == 'news_list_mk':
					if Selenium.parse_module[module]['activated']:
						self.__crawl_news_mk(module)


		except Exception as e:
			print(f'error : {e}')
			traceback.print_exc()

			# error cnt up
			Selenium.errjobs_newscrawl += 1

			try:
				self.driver.close()
				# reload
				self.driver = webdriver.Chrome('./static/chromedriver', chrome_options=Selenium.options)
				self.driver.implicitly_wait(3)
			except:
				pass

	def __crawl_news_naver(self, module):
		"""sub method to crawl naver news"""

		tmp_alter = Selenium.parse_method[Selenium.parse_module[module]['alter']]
		assert isinstance(tmp_alter, dict)

		# @ select date range
		for i in range(0, Selenium.parse_module[module]['date_back'], 1):

			# @ get end page
			pDate = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")

			# url now
			urlNow = Selenium.parse_module[module]['url']
			url1 , url2 = urlNow.split(tmp_alter['date'])
			url2,  url3 = url2.split(tmp_alter['page'])

			# @ targ url
			targUrl = url1 + tmp_alter['date'] + pDate + tmp_alter['page']

			# @ set Selenium driver
			tmp_pgUrl_res = self.__findTagElement(
												  module=module,
												  methodString= '//td[@class="pgRR"]/a[@href]',
												  targUrl=targUrl + '1'
												  ).get_attribute('href')

			# @ final page
			_, pFinal = tmp_pgUrl_res.split(tmp_alter['page'])

			# @ iter pages in the date
			for pg in range(int(1), int(pFinal), 1):

				# @ targ url
				realTargUrl = targUrl + str(pg)

				# set url
				self.__getDriver(url=realTargUrl)

				# get pg source
				tmp_htmlSource = self.driver.page_source
				soup = BeautifulSoup(tmp_htmlSource, 'lxml')
				tmp_targVar = soup.find_all("dd", attrs={"class": "articleSubject"})
				""" filter url to wanted configuration that can be hashed"""
				tmp_result = [ ('https://finance.naver.com' + data.find("a").attrs.get('href')).split('&mode=')[0]  \
							   for data in tmp_targVar]


				# @ iter found article urls
				for aUrl in tmp_result:
					#https://finance.naver.com/news/news_read.nhn?article_id=0004760077&office_id=009&mode=LSS2D&type=0&section_id=101&section_id2=258&section_id3=&date=20210308&page=1

					# @ look up data table
					if aUrl in Selenium.pResult['news_list']:
						continue # skip existing record from memory

					# @ if not
					# set url & get source
					self.__getDriver(url=aUrl)
					tmp_htmlSource = self.driver.page_source
					Selenium.pResult['news_list'][aUrl] = NewsData_Naver(pgSource=tmp_htmlSource, url=aUrl,
																		 date_len=Selenium.parse_module['news_list_naver']['date_back'] )

				# @ eraise if date is exceeded
				cpyDict = {key:value._keep_data() for key, value in zip(Selenium.pResult['news_list'].keys(), Selenium.pResult['news_list'].values())}
				for (key, value) in cpyDict.items():
					if value == False:
						Selenium.pResult['news_list'].pop(key, None) # if not correct key, return None



	def __crawl_news_mk(self, module):
		"""sub method to crawl mail-k news"""
		pass




if __name__ =='__main__':
	import traceback
	try:
		tmp_cls = Selenium()
		tmp_cls._craw_news()
	except Exception as e:
		print(e)
		traceback.print_exc()

