from django.urls import path, include
from . import views

urlpatterns = [
    path('stock20/', views.message_getStock20),
    path('stockLookup/', views.message_lookup),
]