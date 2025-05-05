from django import forms
from django.core.exceptions import ValidationError
from .models import Category, Product, Client, Sale, SaleItem, StockMovement, Payment, StockMovementItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'code_prefix']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code_prefix': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'description', 'category', 'sale_price', 'cost_price', 
                  'min_stock', 'supplier', 'image']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'cpf_cnpj', 'phone', 'address', 'email', 'credit_limit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control'})
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['code', 'client', 'payment_method', 'status', 'notes']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select', 'onchange': 'updateProductInfo(this)'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'onchange': 'updateTotalPrice()'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'onchange': 'updateTotalPrice()'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show products with stock available
        self.fields['product'].queryset = Product.objects.filter(stock_quantity__gt=0)
        
        # If instance exists, include the current product even if out of stock
        if self.instance and self.instance.pk:
            self.fields['product'].queryset = self.fields['product'].queryset | Product.objects.filter(pk=self.instance.product.pk)
        
        # Set initial unit_price if product is selected
        if 'product' in self.data:
            try:
                product_id = int(self.data.get('product'))
                product = Product.objects.get(pk=product_id)
                self.fields['unit_price'].initial = product.sale_price
            except (ValueError, TypeError, Product.DoesNotExist):
                pass
        elif self.instance and self.instance.pk:
            self.fields['unit_price'].initial = self.instance.unit_price
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        
        if product and quantity:
            # If editing existing item, check only additional quantity
            additional_qty = quantity
            if self.instance and self.instance.pk:
                additional_qty = quantity - self.instance.quantity
            
            if additional_qty > 0 and additional_qty > product.stock_quantity:
                raise ValidationError(f'Estoque insuficiente. Disponível: {product.stock_quantity}')
        
        return cleaned_data

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'notes']
        labels = {
            'movement_type': 'Tipo de Movimentação',
            'notes': 'Observações'
        }
        widgets = {
            'movement_type': forms.Select(choices=StockMovement.MOVEMENT_TYPES),
            'notes': forms.Textarea(attrs={'rows': 3})
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['client', 'sale', 'amount', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'sale': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show pending sales
        self.fields['sale'].queryset = Sale.objects.filter(status='pendente')
        
        # If client is selected, filter sales by client
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['sale'].queryset = Sale.objects.filter(client_id=client_id, status='pendente')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['sale'].queryset = Sale.objects.filter(client=self.instance.client, status='pendente')

class SaleSearchForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(choices=[('', 'Todos')] + list(Sale.STATUS_CHOICES), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    payment_method = forms.ChoiceField(choices=[('', 'Todos')] + list(Sale.PAYMENT_CHOICES), required=False, widget=forms.Select(attrs={'class': 'form-select'}))

class ProductSearchForm(forms.Form):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    low_stock = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class ClientSearchForm(forms.Form):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do cliente'}))
    has_debt = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class StockMovementItemForm(forms.ModelForm):
    class Meta:
        model = StockMovementItem
        fields = ['product', 'quantity']
        labels = {
            'product': 'Produto',
            'quantity': 'Quantidade'
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        movement = self.instance.movement if self.instance.pk else None
        
        if product and quantity and movement:
            if movement.movement_type == 'saida' and quantity > product.stock_quantity:
                raise ValidationError(f'Estoque insuficiente. Disponível: {product.stock_quantity}')
        
        return cleaned_data

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }