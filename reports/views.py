from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField
from django.utils import timezone
from datetime import datetime, timedelta
from .models import SalesReport, TopProductsReport, TopProductsItem
from store.models import Sale, SaleItem, Product

class SalesReportListView(ListView):
    model = SalesReport
    template_name = 'reports/sales_report_list.html'
    context_object_name = 'reports'

class SalesReportCreateView(CreateView):
    model = SalesReport
    template_name = 'reports/sales_report_form.html'
    fields = ['start_date', 'end_date']
    success_url = reverse_lazy('sales_report_list')

    def form_valid(self, form):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        
        # Calcula as métricas do relatório
        sales = Sale.objects.filter(
            date__date__range=[start_date, end_date],
            status='pago'
        )
        
        total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
        total_items = SaleItem.objects.filter(
            sale__in=sales
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Calcula o lucro total
        total_profit = 0
        for sale in sales:
            for item in sale.items.all():
                profit = (float(item.unit_price) - float(item.product.cost_price)) * item.quantity
                total_profit += profit
        
        # Cria o relatório
        report = form.save(commit=False)
        report.total_sales = total_sales
        report.total_profit = total_profit
        report.total_items = total_items
        report.save()
        
        return super().form_valid(form)

class TopProductsReportListView(ListView):
    model = TopProductsReport
    template_name = 'reports/top_products_report_list.html'
    context_object_name = 'reports'

class TopProductsReportCreateView(CreateView):
    model = TopProductsReport
    template_name = 'reports/top_products_report_form.html'
    fields = ['start_date', 'end_date']
    success_url = reverse_lazy('top_products_report_list')

    def form_valid(self, form):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        
        # Cria o relatório
        report = form.save()
        
        # Obtém os produtos mais vendidos no período
        top_products = SaleItem.objects.filter(
            sale__date__date__range=[start_date, end_date],
            sale__status='pago'
        ).values(
            'product'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price'),
            profit=Sum(
                ExpressionWrapper(
                    F('quantity') * (F('unit_price') - F('product__cost_price')),
                    output_field=FloatField()
                )
            )
        ).order_by('-total_quantity')[:10]
        
        # Cria os itens do relatório
        for item in top_products:
            TopProductsItem.objects.create(
                report=report,
                product_id=item['product'],
                quantity_sold=item['total_quantity'],
                total_revenue=item['total_revenue'],
                profit=item['profit']
            )
        
        return super().form_valid(form)

class DashboardView(ListView):
    template_name = 'reports/dashboard.html'
    context_object_name = 'metrics'

    def get_queryset(self):
        # Período dos últimos 30 dias
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Vendas do período
        sales = Sale.objects.filter(
            date__range=[start_date, end_date],
            status='pago'
        )
        
        # Métricas principais
        total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
        total_items = SaleItem.objects.filter(
            sale__in=sales
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Produtos mais vendidos
        top_products = SaleItem.objects.filter(
            sale__in=sales
        ).values(
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')[:5]
        
        # Vendas por dia
        daily_sales = sales.values(
            'date__date'
        ).annotate(
            total=Sum('total_amount')
        ).order_by('date__date')
        
        return {
            'total_sales': total_sales,
            'total_items': total_items,
            'top_products': top_products,
            'daily_sales': daily_sales,
            'start_date': start_date,
            'end_date': end_date
        }
