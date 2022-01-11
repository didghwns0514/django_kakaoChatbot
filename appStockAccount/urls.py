from . import views
from django.urls import path

urlpatterns = [
	path('', views.index, name="index"),
	path('signup/', views.signup, name='가입'),
	path('login/', views.login),
	path('check2/', views.index_check),
]