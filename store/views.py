from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta
import json

from .models import Category, Product, Client, Sale, SaleItem, StockMovement, Payment
from .forms import (CategoryForm, ProductForm, ClientForm, SaleForm, SaleItemForm, 
                   StockMovementForm, PaymentForm, SaleSearchForm, ProductSearchForm, ClientSearchForm)

@login_required
def dashboard(request):
    # Get date range for filtering
    today = timezone.now().date()
    start_date = request.GET.get('start_date', (today - timedelta(days=30)).isoformat())
    end_date = request.GET.get('end_date', today.isoformat())
    
    # Convert to datetime for filtering
    start_datetime = timezone.datetime.fromisoformat(start_date)
    end_datetime = timezone.datetime.fromisoformat(end_date) + timedelta(days=1)  # Include the end date
    
    # Sales statistics
    sales_in_period = Sale.objects.filter(date__gte=start_datetime, date__lt=end_datetime)
    total_sales = sales_in_period.count()
    total_revenue = sales_in_period.filter(status='pago').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_sales = sales_in_period.filter(status='pendente').count()
    pending_amount = sales_in_period.filter(status='pendente').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Daily sales chart data
    daily_sales = sales_in_period.annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total=Sum('total_amount')
    ).order_by('day')
    
    # Top selling products
    top_products = SaleItem.objects.filter(
        sale__date__gte=start_datetime, 
        sale__date__lt=end_datetime,
        sale__status__in=['pago', 'pendente']
    ).values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum('total_price')
    ).order_by('-total_quantity')[:5]
    
    # Low stock products
    low_stock_products = Product.objects.filter(stock_quantity__lte=F('min_stock')).order_by('stock_quantity')[:5]
    
    # Clients with highest debt
    clients_with_debt = Client.objects.annotate(
        debt=Sum('sales__total_amount', filter=Q(sales__status='pendente'))
    ).filter(debt__gt=0).order_by('-debt')[:5]
    
    # Sales by payment method
    sales_by_payment = sales_in_period.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-total')
    
    context = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'pending_sales': pending_sales,
        'pending_amount': pending_amount,
        'daily_sales': list(daily_sales),
        'top_products': top_products,
        'low_stock_products': low_stock_products,
        'clients_with_debt': clients_with_debt,
        'sales_by_payment': sales_by_payment,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'store/dashboard.html', context)

# Category views
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category/list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'store/category/form.html', {'form': form, 'title': 'Nova Categoria'})

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'store/category/form.html', {'form': form, 'title': 'Editar Categoria'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Categoria excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir a categoria: {str(e)}')
        return redirect('category_list')
    
    return render(request, 'store/category/confirm_delete.html', {'category': category})

# Product views
@login_required
def product_list(request):
    form = ProductSearchForm(request.GET)
    products = Product.objects.all()
    
    if form.is_valid():
        name = form.cleaned_data.get('name')
        category = form.cleaned_data.get('category')
        low_stock = form.cleaned_data.get('low_stock')
        
        if name:
            products = products.filter(Q(name__icontains=name) | Q(code__icontains=name))
        if category:
            products = products.filter(category=category)
        if low_stock:
            products = products.filter(stock_quantity__lte=F('min_stock'))
    
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/product/list.html', {'page_obj': page_obj, 'form': form})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    stock_movements = product.stock_movements.all().order_by('-date')[:10]
    sales = SaleItem.objects.filter(product=product).order_by('-sale__date')[:10]
    
    return render(request, 'store/product/detail.html', {
        'product': product,
        'stock_movements': stock_movements,
        'sales': sales
    })

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Create initial stock movement
            if product.stock_quantity > 0:
                StockMovement.objects.create(
                    product=product,
                    quantity=product.stock_quantity,
                    movement_type='entrada',
                    reason='Estoque inicial'
                )
            
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'store/product/form.html', {'form': form, 'title': 'Novo Produto'})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    old_stock = product.stock_quantity
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            
            # Create stock movement if stock quantity changed
            new_stock = product.stock_quantity
            if new_stock != old_stock:
                difference = new_stock - old_stock
                movement_type = 'entrada' if difference > 0 else 'saida'
                
                StockMovement.objects.create(
                    product=product,
                    quantity=abs(difference),
                    movement_type=movement_type,
                    reason='Ajuste manual de estoque'
                )
            
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'store/product/form.html', {'form': form, 'title': 'Editar Produto'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Produto excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir o produto: {str(e)}')
        return redirect('product_list')
    
    return render(request, 'store/product/confirm_delete.html', {'product': product})

# Client views
@login_required
def client_list(request):
    form = ClientSearchForm(request.GET)
    clients = Client.objects.all()
    
    if form.is_valid():
        name = form.cleaned_data.get('name')
        has_debt = form.cleaned_data.get('has_debt')
        
        if name:
            clients = clients.filter(Q(name__icontains=name) | Q(code__icontains=name) | Q(cpf_cnpj__icontains=name))
        
        if has_debt:
            clients_with_debt = []
            for client in clients:
                if client.total_debt > 0:
                    clients_with_debt.append(client.id)
            clients = clients.filter(id__in=clients_with_debt)
    
    paginator = Paginator(clients, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/client/list.html', {'page_obj': page_obj, 'form': form})

@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    sales = client.sales.all().order_by('-date')
    payments = client.payments.all().order_by('-payment_date')
    
    return render(request, 'store/client/detail.html', {
        'client': client,
        'sales': sales,
        'payments': payments
    })

@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente criado com sucesso!')
            return redirect('client_list')
    else:
        form = ClientForm()
    
    return render(request, 'store/client/form.html', {'form': form, 'title': 'Novo Cliente'})

@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'store/client/form.html', {'form': form, 'title': 'Editar Cliente'})

@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        try:
            client.delete()
            messages.success(request, 'Cliente excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir o cliente: {str(e)}')
        return redirect('client_list')
    
    return render(request, 'store/client/confirm_delete.html', {'client': client})

# Sale views
@login_required
def sale_list(request):
    form = SaleSearchForm(request.GET)
    sales = Sale.objects.all()
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        client = form.cleaned_data.get('client')
        status = form.cleaned_data.get('status')
        payment_method = form.cleaned_data.get('payment_method')
        
        if start_date:
            sales = sales.filter(date__gte=timezone.datetime.combine(start_date, timezone.datetime.min.time()))
        if end_date:
            sales = sales.filter(date__lte=timezone.datetime.combine(end_date, timezone.datetime.max.time()))
        if client:
            sales = sales.filter(client=client)
        if status:
            sales = sales.filter(status=status)
        if payment_method:
            sales = sales.filter(payment_method=payment_method)
    
    paginator = Paginator(sales, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/sale/list.html', {'page_obj': page_obj, 'form': form})

@login_required
def sale_detail(request, pk):
    # Obtém o objeto Sale ou retorna 404 caso não exista
    sale = get_object_or_404(Sale, pk=pk)
    
    # Obtém os itens da venda
    items = sale.items.all()
    
    # Obtém os pagamentos da venda
    payments = sale.payments.all()

    # Calculando o total dos itens (ajuste conforme o modelo)
    total_sale = items.aggregate(total_amount=Sum('unit_price'))['total_amount'] or 0 # Caso os itens tenham preço

    # Calculando o total pago
    total_paid = payments.aggregate(total_paid=Sum('amount'))['total_paid'] or 0  # Caso o modelo de pagamento tenha um campo 'amount'

    # Calculando o saldo devedor
    total_due = total_sale - total_paid

    # Passando as variáveis para o template
    return render(request, 'store/sale/detail.html', {
        'sale': sale,
        'items': items,
        'payments': payments,
        'total_sale': total_sale,
        'total_paid': total_paid,
        'total_due': total_due,
    })

@login_required
def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            
            # Se a forma de pagamento for 'prazo', define o status como 'pendente'
            if sale.payment_method == 'prazo':
                sale.status = 'pendente'
            else:
                sale.status = 'pago'  # ou outro valor conforme sua lógica
            
            sale.save()
            messages.success(request, 'Venda criada com sucesso! Adicione os produtos.')
            return redirect('sale_item_create', sale_id=sale.id)
    else:
        # Gera o próximo código de venda
        last_sale = Sale.objects.order_by('-id').first()
        next_code = 'V0001'
        if last_sale:
            last_code = last_sale.code
            if last_code.startswith('V'):
                try:
                    num = int(last_code[1:]) + 1
                    next_code = f'V{num:04d}'
                except ValueError:
                    pass
        
        form = SaleForm(initial={'code': next_code})
    
    return render(request, 'store/sale/form.html', {'form': form, 'title': 'Nova Venda'})


@login_required
def sale_update(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venda atualizada com sucesso!')
            return redirect('sale_detail', pk=sale.id)
    else:
        form = SaleForm(instance=sale)
    
    return render(request, 'store/sale/form.html', {'form': form, 'title': 'Editar Venda'})

@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        try:
            # Change status to canceled instead of deleting
            sale.status = 'cancelado'
            sale.save()
            messages.success(request, 'Venda cancelada com sucesso!')
        except Exception as e:
            messages.error(request, f'Não foi possível cancelar a venda: {str(e)}')
        return redirect('sale_list')
    
    return render(request, 'store/sale/confirm_delete.html', {'sale': sale})

@login_required
def sale_item_create(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)
    items = sale.items.all()
    
    if request.method == 'POST':
        form = SaleItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.sale = sale
            item.save()
            messages.success(request, 'Item adicionado com sucesso!')
            return redirect('sale_item_create', sale_id=sale.id)
    else:
        form = SaleItemForm()
    
    return render(request, 'store/sale/items.html', {
        'form': form,
        'sale': sale,
        'items': items
    })

@login_required
def sale_item_delete(request, pk):
    item = get_object_or_404(SaleItem, pk=pk)
    sale_id = item.sale.id
    
    if request.method == 'POST':
        try:
            # Restore stock
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
            
            # Delete item
            item.delete()
            messages.success(request, 'Item removido com sucesso!')
        except Exception as e:
            messages.error(request, f'Não foi possível remover o item: {str(e)}')
        return redirect('sale_item_create', sale_id=sale_id)
    
    return render(request, 'store/sale/confirm_delete_item.html', {'item': item})

@login_required
def sale_finalize(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        if not sale.items.exists():
            messages.error(request, 'Não é possível finalizar uma venda sem itens!')
            return redirect('sale_item_create', sale_id=sale.id)
        
        # If payment is not 'prazo', mark as paid
        if sale.payment_method != 'prazo':
            sale.status = 'pago'
            sale.save()
        
        messages.success(request, 'Venda finalizada com sucesso!')
        return redirect('sale_detail', pk=sale.id)
    
    return render(request, 'store/sale/finalize.html', {'sale': sale})

# Stock Movement views
@login_required
def stock_movement_list(request):
    movements = StockMovement.objects.all().order_by('-date')
    
    paginator = Paginator(movements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/stock/list.html', {'page_obj': page_obj})

@login_required
def stock_movement_create(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Movimento de estoque registrado com sucesso!')
            return redirect('stock_movement_list')
    else:
        form = StockMovementForm()
    
    return render(request, 'store/stock/form.html', {'form': form, 'title': 'Novo Movimento de Estoque'})

# Payment views
@login_required
def payment_list(request):
    payments = Payment.objects.all().order_by('-payment_date')
    
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/payment/list.html', {'page_obj': page_obj})

@login_required
def payment_create(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pagamento registrado com sucesso!')
            return redirect('payment_list')
    else:
        form = PaymentForm()
    
    return render(request, 'store/payment/form.html', {'form': form, 'title': 'Novo Pagamento'})

@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        try:
            # If payment was for a sale, update sale status
            sale = payment.sale
            if sale:
                sale.status = 'pendente'
                sale.save()
            
            payment.delete()
            messages.success(request, 'Pagamento excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir o pagamento: {str(e)}')
        return redirect('payment_list')
    
    return render(request, 'store/payment/confirm_delete.html', {'payment': payment})

# Report views
@login_required
def report_sales(request):
    # Get date range for filtering
    today = timezone.now().date()
    start_date = request.GET.get('start_date', (today - timedelta(days=30)).isoformat())
    end_date = request.GET.get('end_date', today.isoformat())
    
    # Convert to datetime for filtering
    start_datetime = timezone.datetime.fromisoformat(start_date)
    end_datetime = timezone.datetime.fromisoformat(end_date) + timedelta(days=1)  # Include the end date
    
    # Get sales in period
    sales = Sale.objects.filter(date__gte=start_datetime, date__lt=end_datetime)
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        sales = sales.filter(status=status)
    
    # Calculate totals
    total_amount = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_count = sales.count()
    
    # Group by day
    sales_by_day = sales.annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('day')
    
    # Group by payment method
    sales_by_payment = sales.values('payment_method').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'sales': sales,
        'total_amount': total_amount,
        'total_count': total_count,
        'sales_by_day': sales_by_day,
        'sales_by_payment': sales_by_payment,
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
    }
    
    return render(request, 'store/reports/sales.html', context)

@login_required
def report_products(request):
    # Get date range for filtering
    today = timezone.now().date()
    start_date = request.GET.get('start_date', (today - timedelta(days=30)).isoformat())
    end_date = request.GET.get('end_date', today.isoformat())
    
    # Convert to datetime for filtering
    start_datetime = timezone.datetime.fromisoformat(start_date)
    end_datetime = timezone.datetime.fromisoformat(end_date) + timedelta(days=1)  # Include the end date
    
    # Top selling products
    top_products = SaleItem.objects.filter(
        sale__date__gte=start_datetime, 
        sale__date__lt=end_datetime,
        sale__status__in=['pago', 'pendente']
    ).values(
        'product__id',
        'product__name',
        'product__code',
        'product__category__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum('total_price'),
        profit=Sum(
            ExpressionWrapper(
                F('total_price') - (F('quantity') * F('product__cost_price')),
                output_field=DecimalField()
            )
        )
    ).order_by('-total_quantity')
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        top_products = top_products.filter(product__category_id=category_id)
    
    # Get all categories for filter
    categories = Category.objects.all()
    
    context = {
        'top_products': top_products,
        'categories': categories,
        'start_date': start_date,
        'end_date': end_date,
        'selected_category': category_id,
    }
    
    return render(request, 'store/reports/products.html', context)

@login_required
def report_clients(request):
    # Get clients with sales and debt information
    clients = Client.objects.annotate(
        total_purchases=Count('sales', filter=Q(sales__status__in=['pago', 'pendente'])),
        total_spent=Sum('sales__total_amount', filter=Q(sales__status__in=['pago', 'pendente'])),
        debt=Sum('sales__total_amount', filter=Q(sales__status='pendente'))
    ).filter(total_purchases__gt=0)
    
    # Filter by debt status if provided
    debt_status = request.GET.get('debt_status')
    if debt_status == 'with_debt':
        clients = clients.filter(debt__gt=0)
    elif debt_status == 'no_debt':
        clients = clients.filter(Q(debt=0) | Q(debt__isnull=True))
    
    context = {
        'clients': clients,
        'debt_status': debt_status,
    }
    
    return render(request, 'store/reports/clients.html', context)

@login_required
def report_stock(request):
    # Get all products with stock information
    products = Product.objects.all().order_by('category__name', 'name')
    
    # Filter by stock status if provided
    stock_status = request.GET.get('stock_status')
    if stock_status == 'low_stock':
        products = products.filter(stock_quantity__lte=F('min_stock'))
    elif stock_status == 'out_of_stock':
        products = products.filter(stock_quantity=0)
    elif stock_status == 'in_stock':
        products = products.filter(stock_quantity__gt=F('min_stock'))
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Get all categories for filter
    categories = Category.objects.all()
    
    # Calculate totals
    total_products = products.count()
    total_stock_value = sum(p.stock_quantity * p.cost_price for p in products)
    low_stock_count = products.filter(stock_quantity__lte=F('min_stock')).count()
    
    context = {
        'products': products,
        'categories': categories,
        'stock_status': stock_status,
        'selected_category': category_id,
        'total_products': total_products,
        'total_stock_value': total_stock_value,
        'low_stock_count': low_stock_count,
    }
    
    return render(request, 'store/reports/stock.html', context)

# API views for AJAX
@login_required
def api_get_product_info(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return JsonResponse({
        'sale_price': float(product.sale_price),
        'stock_quantity': product.stock_quantity
    })

@login_required
def api_get_client_sales(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    sales = Sale.objects.filter(client=client, status='pendente')
    
    sales_data = []
    for sale in sales:
        sales_data.append({
            'id': sale.id,
            'code': sale.code,
            'date': sale.date.strftime('%d/%m/%Y'),
            'total_amount': float(sale.total_amount)
        })
    
    return JsonResponse({'sales': sales_data})