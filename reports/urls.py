from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('sales/', views.SalesReportListView.as_view(), name='sales_report_list'),
    path('sales/create/', views.SalesReportCreateView.as_view(), name='sales_report_create'),
    path('top-products/', views.TopProductsReportListView.as_view(), name='top_products_report_list'),
    path('top-products/create/', views.TopProductsReportCreateView.as_view(), name='top_products_report_create'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
] 