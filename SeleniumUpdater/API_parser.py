from parseapp.models import StockListData
from SeleniumUpdater.Parser import Selenium

new_selObj = Selenium()

def update_parser_1():

	#new_selObj = SeleniumUpdater()
	result_dict = new_selObj._crawl_stock_list()

	try:
		new_obj = StockListData()

		# update
		for stockName_key in result_dict:
			new_obj.source = result_dict[stockName_key]['source']
			new_obj.num = result_dict[stockName_key]['num']
			new_obj.name = result_dict[stockName_key]['name']
			new_obj.price_now = result_dict[stockName_key]['priceNow']
			new_obj.price_compared = result_dict[stockName_key]['priceCompared']
			new_obj.price_ratio = result_dict[stockName_key]['priceRatio']
			new_obj.price_straight = result_dict[stockName_key]['priceStraight']
			new_obj.total_stock_sum = result_dict[stockName_key]['totalStockSum']
			new_obj.total_stock_num = result_dict[stockName_key]['totalStockNum']
			new_obj.total_foreign_ratio = result_dict[stockName_key]['totalForeignRatio']
			new_obj.trade_sum = result_dict[stockName_key]['tradeSum']
			new_obj.per = result_dict[stockName_key]['PER']
			new_obj.roe = result_dict[stockName_key]['ROE']

			# new_obj.temperatue = temp_in_celsius
			# new_obj.description = json['weather'][0]['description']
			# new_obj.city = json['name']

			# save
			new_obj.save()
			#print("saving...\n" + new_obj)
	except:
		pass


def update_parser_test():
	from datetime import datetime
	print(f'datetime now : {datetime.now()}')