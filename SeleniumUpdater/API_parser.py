from parseapp.models import StockListData
from SeleniumUpdater.Parser import Selenium
from django.db.models import Q
from datetime import *

import traceback

new_selObj = Selenium()

class UpdateState:

	TOTAL_COL = ['source','num','name','price_now','price_compared','price_ratio',
				 'price_straight','total_stock_sum','total_stock_num','total_foreign_ratio',
				 'trade_sum','per','roe']

	NEW_COL = ['price_now','price_compared','price_ratio', 'total_foreign_ratio',
			   'trade_sum']

	LAST_UPDATE = None
	SAFE_BATCH = 20
	ORI_BATCH = 999

	@staticmethod
	def get():
		"""return column and batch size"""
		if UpdateState.LAST_UPDATE == None: # never parsed before
			UpdateState.LAST_UPDATE = datetime.now()
			return int(UpdateState.SAFE_BATCH), UpdateState.TOTAL_COL
		else:
			if datetime.now() - timedelta(hours=7) >= UpdateState.LAST_UPDATE: # exceeded time limit
				UpdateState.LAST_UPDATE = datetime.now()
				return int(UpdateState.SAFE_BATCH), UpdateState.TOTAL_COL
			else:

				return int(UpdateState.ORI_BATCH // (len(UpdateState.NEW_COL)*2.5)), UpdateState.NEW_COL

def update_parser_1():

	#new_selObj = SeleniumUpdater()
	result_dict = new_selObj._crawl_stock_list()

	try:

		tmp_stockName_key = list(result_dict.keys())

		# https://yongbeomkim.github.io/django/dj-filter-orm-basic/
		djangoORM = [StockListData.objects.filter(Q(name__iexact=_name)) \
					 for _name in tmp_stockName_key ]
		tmp_update = [ djangoORM[n][0] for n, stkName in enumerate(tmp_stockName_key) if djangoORM[n] ]
		tmp_create = [ stkName for n, stkName in enumerate(tmp_stockName_key) if not djangoORM[n] ]
		#
		# print(f'tmp_update : {tmp_update}')
		# print(f'tmp_create : {tmp_create}')

		# for _item in tmp_update:
		# 	print(f'type of _item : {type(_item)}')
		# 	print(f'_item : {_item}')
		# 	for sub in _item:
		# 		print(f'type of sub : {type(sub)}')
		# 		print(f'sub : {sub}')

		# @ update
		for tORM in tmp_update:
			stockName_key = tORM.name #tORM.values()[0]['name']
			tORM.source = result_dict[stockName_key]['source']
			tORM.num = result_dict[stockName_key]['num']
			tORM.name = result_dict[stockName_key]['name']
			tORM.price_now = result_dict[stockName_key]['priceNow']
			tORM.price_compared = result_dict[stockName_key]['priceCompared']
			tORM.price_ratio = result_dict[stockName_key]['priceRatio']
			tORM.price_straight = result_dict[stockName_key]['priceStraight']
			tORM.total_stock_sum = result_dict[stockName_key]['totalStockSum']
			tORM.total_stock_num = result_dict[stockName_key]['totalStockNum']
			tORM.total_foreign_ratio = result_dict[stockName_key]['totalForeignRatio']
			tORM.trade_sum = result_dict[stockName_key]['tradeSum']
			tORM.per = result_dict[stockName_key]['PER']
			tORM.roe = result_dict[stockName_key]['ROE']

		_batch_size, col_names = UpdateState.get()
		for k in range( int( len(tmp_update)//_batch_size)+1 ):
			print(f'k : {k}')
			print(f'k*_batch_size : {k*_batch_size}')
			print(f'(k+1)*_batch_size : {(k+1)*_batch_size}')
			print(f'size chosen : {len(tmp_update[k*_batch_size : (k+1)*_batch_size])}')
			StockListData.objects.bulk_update(tmp_update[k*_batch_size : (k+1)*_batch_size],
											  col_names)
		StockListData.objects.all().update(timestamp=datetime.now())

		# @ create
		_bulk_create = []
		for stockName_key in tmp_create:
			tmp_ORM = StockListData()
			tmp_ORM.source = result_dict[stockName_key]['source']
			tmp_ORM.num = result_dict[stockName_key]['num']
			tmp_ORM.name = result_dict[stockName_key]['name']
			tmp_ORM.price_now = result_dict[stockName_key]['priceNow']
			tmp_ORM.price_compared = result_dict[stockName_key]['priceCompared']
			tmp_ORM.price_ratio = result_dict[stockName_key]['priceRatio']
			tmp_ORM.price_straight = result_dict[stockName_key]['priceStraight']
			tmp_ORM.total_stock_sum = result_dict[stockName_key]['totalStockSum']
			tmp_ORM.total_stock_num = result_dict[stockName_key]['totalStockNum']
			tmp_ORM.total_foreign_ratio = result_dict[stockName_key]['totalForeignRatio']
			tmp_ORM.trade_sum = result_dict[stockName_key]['tradeSum']
			tmp_ORM.per = result_dict[stockName_key]['PER']
			tmp_ORM.roe = result_dict[stockName_key]['ROE']

			_bulk_create.append(tmp_ORM)
		StockListData.objects.bulk_create(_bulk_create)

		print(f'reached end of the job...')
	except Exception as e:
		print(f'error in API parser : {e}')
		traceback.print_exc()


def update_parser_test():
	from datetime import datetime
	print(f'datetime now : {datetime.now()}')