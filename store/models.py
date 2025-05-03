from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, Q
from django.urls import reverse

class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    code_prefix = models.CharField(max_length=2, unique=True, verbose_name="Prefixo do Código")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Product model"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Código", blank=True, db_index=True)
    name = models.CharField(max_length=100, verbose_name="Nome", db_index=True)
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name="Categoria")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Preço de Venda")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Preço de Custo")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Quantidade em Estoque", db_index=True)
    min_stock = models.PositiveIntegerField(default=5, verbose_name="Estoque Mínimo")
    supplier = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fornecedor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Imagem")
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'code']),
            models.Index(fields=['stock_quantity']),
            models.Index(fields=['category', 'stock_quantity']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Otimização: Evitar múltiplas queries ao banco
        if not self.code and self.category:
            # Usar uma única query para obter o último produto
            last_product = Product.objects.filter(
                category=self.category
            ).only('code').order_by('-code').first()
            
            if last_product and last_product.code:
                last_number = int(last_product.code[2:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.code = f"{self.category.code_prefix}{new_number:02d}"
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})
    
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
    
    def save(self, *args, **kwargs):
        # Gera o código automaticamente apenas para novos clientes
        if not self.pk:
            # Busca o último código de cliente
            last_client = Client.objects.order_by('-code').first()
            if last_client and last_client.code.startswith('CLI'):
                try:
                    # Extrai o número do último código e incrementa
                    last_number = int(last_client.code[3:])
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            
            # Formata o novo código com zeros à esquerda
            self.code = f"CLI{new_number:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def total_debt(self):
        """Calculate total debt from unpaid sales minus payments"""
        # Usando cache para evitar múltiplas consultas
        if not hasattr(self, '_total_debt'):
            self._total_debt = (
                self.sales.filter(status='pendente').aggregate(
                    total=Sum('total_amount')
                )['total'] or 0
            ) - (
                self.payments.filter(
                    sale__status='pendente'
                ).aggregate(
                    total=Sum('amount')
                )['total'] or 0
            )
        return self._total_debt

    def clear_debt_cache(self):
        """Clear the cached total_debt value"""
        if hasattr(self, '_total_debt'):
            delattr(self, '_total_debt')
    
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
    )
    
    date = models.DateTimeField(auto_now_add=True)
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.date.strftime('%d/%m/%Y %H:%M')}"
    
    def get_total_items(self):
        return self.items.count()
    
    def get_total_value(self):
        """Calcula o valor total da movimentação"""
        total = 0
        for item in self.items.all():
            total += item.quantity * item.product.cost_price
        return total

class StockMovementItem(models.Model):
    movement = models.ForeignKey(StockMovement, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movement_items')
    quantity = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} unidades"
    
    def save(self, *args, **kwargs):
        # Se for uma atualização, primeiro revertemos a quantidade anterior
        if self.pk:
            old_item = StockMovementItem.objects.get(pk=self.pk)
            if old_item.movement.movement_type == 'entrada':
                self.product.stock_quantity -= old_item.quantity
            else:
                self.product.stock_quantity += old_item.quantity
        
        # Agora aplicamos a nova quantidade
        if self.movement.movement_type == 'entrada':
            self.product.stock_quantity += self.quantity
        else:
            self.product.stock_quantity -= self.quantity
        
        # Salvamos o produto primeiro para garantir que o estoque está atualizado
        self.product.save()
        # Depois salvamos o item da movimentação
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Revertemos a quantidade no estoque
        if self.movement.movement_type == 'entrada':
            self.product.stock_quantity -= self.quantity
        else:
            self.product.stock_quantity += self.quantity
        
        # Salvamos o produto primeiro
        self.product.save()
        # Depois deletamos o item
        super().delete(*args, **kwargs)

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