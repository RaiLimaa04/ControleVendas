from django.db import models
from django.utils import timezone

class SalesReport(models.Model):
    """Modelo para armazenar relatórios de vendas"""
    start_date = models.DateField(verbose_name="Data Inicial")
    end_date = models.DateField(verbose_name="Data Final")
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total de Vendas")
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Lucro Total")
    total_items = models.PositiveIntegerField(verbose_name="Total de Itens Vendidos")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Relatório de Vendas"
        verbose_name_plural = "Relatórios de Vendas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Relatório de Vendas - {self.start_date} a {self.end_date}"

class TopProductsReport(models.Model):
    """Modelo para armazenar relatórios de produtos mais vendidos"""
    start_date = models.DateField(verbose_name="Data Inicial")
    end_date = models.DateField(verbose_name="Data Final")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Relatório de Produtos Mais Vendidos"
        verbose_name_plural = "Relatórios de Produtos Mais Vendidos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Produtos Mais Vendidos - {self.start_date} a {self.end_date}"

class TopProductsItem(models.Model):
    """Itens do relatório de produtos mais vendidos"""
    report = models.ForeignKey(TopProductsReport, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, verbose_name="Produto")
    quantity_sold = models.PositiveIntegerField(verbose_name="Quantidade Vendida")
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Receita Total")
    profit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Lucro")
    
    class Meta:
        verbose_name = "Item do Relatório de Produtos"
        verbose_name_plural = "Itens do Relatório de Produtos"
        ordering = ['-quantity_sold']
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity_sold} unidades"
