from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name="index"),
	path('keyboard', views.keyboard, name="keyboard"),
	path('test', views.test, name="test"),
	path('message_news', views.message_news, name="message_news"),
	path('message_merge', views.message_merge, name="message_merge"),
	path('message_stock', views.message_stock, name="message_stock"),
	path('mainpage', views.MainPage.as_view(), name="mainpage")
]