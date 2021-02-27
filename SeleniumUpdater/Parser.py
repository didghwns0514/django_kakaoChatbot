"""
	Parser

	to check how to use xpath
	>>> https://www.w3schools.com/xml/xpath_syntax.asp

"""

from selenium import webdriver
from bs4 import BeautifulSoup
from Configuration import *
import lxml

class Selenium:

	# @ setup args
	options = webdriver.ChromeOptions()
	args = ['headless', 'window-size=1920x1080', 'disable-gpu',
			"user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"]
	for arg in args:
		options.add_argument(arg)

	# @ driver
	driver = webdriver.Chrome('./static/chromedriver', chrome_options=options)
	driver.implicitly_wait(3)
	dResult = None

	flags = {
		'stock_list':False,
		'news_list':False
	}
	parse_method = {'page' : '&page='}
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
						'source' : '코스닥'
						},
		'news_list' : {
		}
	}
	pResult = {
		'stock_list_kospi' : {},
		'stock_list_kosdaq' : {},
		'news_list' : {}
	}

	@staticmethod
	def __getDriver(url:str):
		"""load driver a url"""
		try:
			# print(f'SeleniumUpdater.driver : {SeleniumUpdater.driver}')
			# print(f'type(SeleniumUpdater.driver) : {type(SeleniumUpdater.driver)}')
			if Selenium.driver.current_url != url:
				Selenium.driver.get(url)
		except:
			pass

	@staticmethod
	def __findTagElement(module:str, methodString:str,targUrl:str=None):
		"""
		method to find tag elements
		:param methodString:
		:return:
		"""
		# @ init
		Selenium.dResult = None

		if targUrl == None: # set target from dictionary
			mode = Selenium.parse_module[module]
			Selenium.__getDriver(mode['url'])
		else:
			Selenium.__getDriver(targUrl)

		Selenium.dResult = Selenium.driver.find_element_by_xpath(methodString)

		return Selenium.dResult


	@staticmethod
	def _crawl_stock_list(state='stock_list'):

		tmp_module_key = [ key_lv1 for key_lv1, val1 in zip(Selenium.parse_module.keys(), Selenium.parse_module.values())
						   if state in key_lv1]

		for module in tmp_module_key:

			tmp_alter = Selenium.parse_method[Selenium.parse_module[module]['alter']]
			# tmp_pgUrl_res = SeleniumUpdater.__findTagElement(module=module,
			# 										  methodString= '//td[@class="pgRR"]/a[@href]'
			# 										  )[0].get_attribute('href')
			tmp_pgUrl_res = Selenium.__findTagElement(module=module,
													  methodString= '//td[@class="pgRR"]/a[@href]'
													  ).get_attribute('href')

			if tmp_pgUrl_res != None : # if the wanted result is parsed

				tmp_href, tmp_last_pg = tmp_pgUrl_res.split(tmp_alter)

				for pg_num in range(1, int(tmp_last_pg) + 1):
					tmp_url = tmp_href + tmp_alter + str(pg_num)

					tmp_targHead = Selenium.__findTagElement(module=module,
															 methodString= \
									'//div[@id="contentarea"]' + \
									'/div[@class]' + \
									'/table[@class="type_2"]' + \
									'/thead/tr',
									 targUrl=tmp_url).find_elements_by_xpath('//th[@scope]')
					tmp_headList = [ obj.text for obj in tmp_targHead ]


					tmp_htmlSource = Selenium.driver.page_source
					soup = BeautifulSoup(tmp_htmlSource, 'lxml')
					tmp_targVar = soup.find("table", attrs={"class": "type_2"}).find("tbody").find_all("tr")
					tmp_varList = []
					_ = [tmp_varList.append(obj.get_text().split()) for obj in tmp_targVar if len(obj.get_text()) > 1]

					# @ append container
					for var_list in tmp_varList:
						tmp_containerCls = StockData(tmp_headList, var_list, source=Selenium.parse_module[module])
						Selenium.pResult[module][tmp_containerCls.name] = tmp_containerCls

				# set the flag up
				Selenium.flags[module] = True

		# when done parsing
		rtn_all_dict = {}
		for module_key in Selenium.pResult:
			for stockName_key in Selenium.pResult[module_key]:
				tmp_cls = Selenium.pResult[module_key][stockName_key]
				rtn_all_dict.update(tmp_cls.__toDict())

		return rtn_all_dict





	@staticmethod
	def _craw_news():
		"""crawl news"""
		pass


if __name__ =='__main__':
	tmp_cls = Selenium()
	tmp_cls._crawl_stock_list()

