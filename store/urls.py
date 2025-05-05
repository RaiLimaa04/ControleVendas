from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, ProductDetailView,
    # ... outros imports ...
)

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='store/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/new/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Products
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/new/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    
    # Clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/new/', views.client_create, name='client_create'),
    path('clients/<int:pk>/edit/', views.client_update, name='client_update'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
    
    # Sales
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/new/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/edit/', views.sale_update, name='sale_update'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale_delete'),
    path('sales/<int:sale_id>/items/', views.sale_item_create, name='sale_item_create'),
    path('sales/items/<int:pk>/delete/', views.sale_item_delete, name='sale_item_delete'),
    path('sales/<int:pk>/finalize/', views.sale_finalize, name='sale_finalize'),
    
    # Stock
    path('stock/', views.stock_movement_list, name='stock_movement_list'),
    path('stock/new/', views.stock_movement_create, name='stock_movement_create'),
    path('stock-movements/', views.StockMovementListView.as_view(), name='stock_movement_list'),
    path('stock-movements/create/', views.StockMovementCreateView.as_view(), name='stock_movement_create'),
    path('stock-movements/<int:pk>/add-items/', views.StockMovementAddItemsView.as_view(), name='stock_movement_add_items'),
    path('stock-movements/<int:pk>/', views.StockMovementDetailView.as_view(), name='stock_movement_detail'),
    path('stock-movements/items/<int:pk>/delete/', views.StockMovementItemDeleteView.as_view(), name='stock_movement_item_delete'),
    
    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/new/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/edit/', views.payment_update, name='payment_update'),
    
    # Reports
    path('reports/sales/', views.report_sales, name='report_sales'),
    path('reports/products/', views.report_products, name='report_products'),
    path('reports/clients/', views.report_clients, name='report_clients'),
    path('reports/stock/', views.report_stock, name='report_stock'),
    
    # API
    path('api/clients/<int:client_id>/sales/', views.api_get_client_sales, name='api_get_client_sales'),
    path('api/products/<int:pk>/info/', views.product_info, name='product_info'),
]