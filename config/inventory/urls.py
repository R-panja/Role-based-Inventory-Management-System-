from django.urls import path
from .views import *

urlpatterns = [
    path('inventory/', product_list, name='inventory_dashboard'),
    path('analytics/', inventory_analytics, name='inventory_analytics'),
]