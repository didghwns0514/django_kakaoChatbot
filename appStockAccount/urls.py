from . import views
from django.urls import path

urlpatterns = [
	path('', views.index, name="index"),
	path('signup/', views.signup),
	path('check1/', views.index),
	path('check2/', views.index_check),
]