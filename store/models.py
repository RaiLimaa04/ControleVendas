from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, Q

class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Product model"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name="Categoria")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Preço de Venda")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Preço de Custo")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Quantidade em Estoque")
    min_stock = models.PositiveIntegerField(default=5, verbose_name="Estoque Mínimo")
    supplier = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fornecedor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Imagem")
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price and float(self.cost_price) > 0:
            return ((float(self.sale_price) - float(self.cost_price)) / float(self.cost_price)) * 100
        return 0
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.stock_quantity <= self.min_stock

class Client(models.Model):
    """Client model"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nome")
    cpf_cnpj = models.CharField(max_length=20, blank=True, null=True, verbose_name="CPF/CNPJ")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    address = models.TextField(blank=True, null=True, verbose_name="Endereço")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Limite de Crédito")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def total_debt(self):
        """Calculate total debt from unpaid sales minus payments"""
        # Get total amount from pending sales
        pending_total = self.sales.filter(status='pendente').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Get total payments for pending sales
        payments_total = self.payments.filter(
            sale__status='pendente'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Return the difference
        return pending_total - payments_total
    
    @property
    def is_over_limit(self):
        """Check if client is over credit limit"""
        return self.total_debt > self.credit_limit and self.credit_limit > 0

class Sale(models.Model):
    """Sale model"""
    STATUS_CHOICES = (
        ('pago', 'Pago'),
        ('pendente', 'Pendente'),
        ('cancelado', 'Cancelado'),
    )
    
    PAYMENT_CHOICES = (
        ('dinheiro', 'Dinheiro'),
        ('cartao', 'Cartão'),
        ('pix', 'PIX'),
        ('prazo', 'A Prazo'),
        ('outro', 'Outro'),
    )
    
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='sales', null=True, blank=True, verbose_name="Cliente")
    date = models.DateTimeField(default=timezone.now, verbose_name="Data e Hora")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Valor Total")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='dinheiro', verbose_name="Forma de Pagamento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pago', verbose_name="Status")
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-date']
    
    def __str__(self):
        return f"Venda {self.code} - {self.date.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # If this is a new sale, update the total amount
        if not self.pk:
            super().save(*args, **kwargs)
        else:
            # If status changed to canceled, restore stock
            old_sale = Sale.objects.get(pk=self.pk)
            if old_sale.status != 'cancelado' and self.status == 'cancelado':
                for item in self.items.all():
                    product = item.product
                    product.stock_quantity += item.quantity
                    product.save()
            super().save(*args, **kwargs)

class SaleItem(models.Model):
    """Sale item model"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name="Venda")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items', verbose_name="Produto")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Quantidade")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Preço Unitário")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Preço Total")
    
    class Meta:
        verbose_name = "Item de Venda"
        verbose_name_plural = "Itens de Venda"
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        
        # If this is a new item, update product stock
        if not self.pk and self.sale.status != 'cancelado':
            self.product.stock_quantity -= self.quantity
            self.product.save()
            
        super().save(*args, **kwargs)
        
        # Update sale total amount
        self.sale.total_amount = self.sale.items.aggregate(models.Sum('total_price'))['total_price__sum'] or 0
        self.sale.save()

class StockMovement(models.Model):
    """Stock movement model"""
    MOVEMENT_TYPES = (
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements', verbose_name="Produto")
    quantity = models.IntegerField(verbose_name="Quantidade")
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name="Tipo de Movimento")
    reason = models.CharField(max_length=100, verbose_name="Motivo")
    date = models.DateTimeField(default=timezone.now, verbose_name="Data e Hora")
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements', verbose_name="Venda Relacionada")
    
    class Meta:
        verbose_name = "Movimento de Estoque"
        verbose_name_plural = "Movimentos de Estoque"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_movement_type_display()} de {self.quantity} unidades de {self.product.name}"
    
    def save(self, *args, **kwargs):
        # If this is a new movement, update product stock
        if not self.pk:
            if self.movement_type == 'entrada':
                self.product.stock_quantity += self.quantity
            elif self.movement_type == 'saida':
                self.product.stock_quantity -= self.quantity
            elif self.movement_type == 'ajuste':
                # For adjustments, quantity can be positive or negative
                self.product.stock_quantity += self.quantity
            
            self.product.save()
            
        super().save(*args, **kwargs)

class Payment(models.Model):
    """Payment model for tracking client payments"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments', verbose_name="Cliente")
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments', null=True, blank=True, verbose_name="Venda")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Valor")
    payment_date = models.DateTimeField(default=timezone.now, verbose_name="Data de Pagamento")
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Pagamento de {self.amount} - {self.client.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # If payment is for a specific sale, update sale status if fully paid
        if self.sale and self.sale.status == 'pendente':
            total_payments = self.sale.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
            if total_payments >= self.sale.total_amount:
                self.sale.status = 'pago'
                self.sale.save()