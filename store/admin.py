from django.contrib import admin
from .models import Category, Product, Client, Sale, SaleItem, StockMovement, Payment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('total_price',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'sale_price', 'stock_quantity', 'is_low_stock')
    list_filter = ('category', 'created_at')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('profit_margin',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'phone', 'total_debt', 'is_over_limit')
    search_fields = ('code', 'name', 'cpf_cnpj', 'phone')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('code', 'client', 'date', 'total_amount', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('code', 'client__name')
    inlines = [SaleItemInline]

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('sale__date',)
    search_fields = ('product__name', 'sale__code')

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'movement_type', 'reason', 'date')
    list_filter = ('movement_type', 'date')
    search_fields = ('product__name', 'reason')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('client', 'sale', 'amount', 'payment_date')
    list_filter = ('payment_date',)
    search_fields = ('client__name', 'sale__code')