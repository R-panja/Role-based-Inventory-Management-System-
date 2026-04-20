from django.urls import path
from .views import manager_dashboard, approve_bill, reject_bill,create_bill,bill_detail,sales_manager_dashboard,report_exception,manager_exceptions
from inventory.views import product_list
from reports.views import *
app_name = 'sales'
urlpatterns = [
    path('manager/', manager_dashboard, name='manager_dashboard'),
    path('approve/<int:bill_id>/', approve_bill, name='approve_bill'),
    path('reject/<int:bill_id>/', reject_bill, name='reject_bill'),
    path('create/',create_bill,name='create_bill'),
    path('bill/<int:bill_id>/', bill_detail, name='bill_detail'),  # ✅ THIS
    path('salesmanager/', sales_manager_dashboard, name='sales_manager_dashboard'),
    # inventory/urls.py
    path('report/', generate_inventory_report, name='inventory_report'),
    # exception handling 
    path('report-exception/', report_exception, name='report_exception'),
    path('manager-exceptions/', manager_exceptions, name='manager_exceptions'),
    
]