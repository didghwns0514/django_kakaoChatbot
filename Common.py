from datetime import datetime, timedelta

"""
https://jahong.tistory.com/entry/CORSCross-Origin-Resource-Sharing%EC%99%80-Django
"""

__SECRET_KEY = '#smrog(f4k4iu*yt!20j7*$z!rt@xn0d9+#ty=oc31=$$%4)sk'
__HOSTS = ['*', u'192.168.0.4', u'localhost', u'219.254.51.182',u'192.168.0.4:5500']
__MY_DB = 	{'default':{
				'NAME' : 'kakaostock',
				'ENGINE' : 'django.db.backends.mysql',
				'USER' : 'root', # user name for login to DB
				'PASSWORD' : 'd@12YinYang',
				'HOST' : 'http://hjyang.iptime.org', # ip, if error use >>>  127.0.0.1
				'PORT' : '44441',
} }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     },
#     # 'db_stock_list':{
#     #     'NAME': 'db.stock_list.sqlite3',
#     #     'ENGINE': 'django.db.backends.sqlite3',
#     # },
#     # 'db_stock_news':{
#     #     'NAME': 'db.stock_news.sqlite3',
#     #     'ENGINE': 'django.db.backends.sqlite3',
#     # }
# }
# #DATABASE_ROUTERS = ['Router.MultiDBRouter',]

def check_timeStamp(dbtime):
	"""functino to check time of db data"""
	timeNorm = datetime.now()
	if timeNorm.weekday() in ['5', '6'] : #sat, sun
		return True
	else:
		if timeNorm >= datetime.now().replace(hour=15, minute=30) \
				or timeNorm <= datetime.now().replace(hour=9, minute=0):
			return True
		else:
			#if timeNorm - datetime.strptime(dbtime, '%Y-%m-%d %H:%M:%S.%f') <= timedelta(minutes=2):
			if timeNorm - dbtime <= timedelta(minutes=2):
				return True
			else:
				return False


def check_opTime(doCheck=False):
	"""check real time operation availability"""
	if not doCheck:
		return True
	else:
		timeNorm = datetime.now()
		if timeNorm.weekday() in ['5', '6'] : #sat, sun
			return False
		else:
			if timeNorm >= datetime.now().replace(hour=15, minute=30) \
					or timeNorm <= datetime.now().replace(hour=9, minute=0):
				return False
			else:
				return True