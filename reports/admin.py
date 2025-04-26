from django.contrib import admin
from .models import SalesReport, TopProductsReport, TopProductsItem

class TopProductsItemInline(admin.TabularInline):
    model = TopProductsItem
    extra = 0
    readonly_fields = ['product', 'quantity_sold', 'total_revenue', 'profit']

@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'end_date', 'total_sales', 'total_profit', 'total_items', 'created_at']
    readonly_fields = ['total_sales', 'total_profit', 'total_items', 'created_at']
    date_hierarchy = 'created_at'

@admin.register(TopProductsReport)
class TopProductsReportAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'end_date', 'created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    inlines = [TopProductsItemInline]
