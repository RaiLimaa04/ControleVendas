import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
import traceback

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_control.settings')
django.setup()

from store.models import Category, Product, Client, Sale, SaleItem
from django.utils import timezone
from django.db import transaction

def create_categories():
    print("Criando categorias...")
    categories = [
        ('AL', 'Alimentos'),
        ('BE', 'Bebidas'),
        ('LI', 'Limpeza'),
        ('PE', 'Perfumaria'),
        ('PA', 'Papelaria'),
    ]
    
    for code, name in categories:
        try:
            category, created = Category.objects.get_or_create(
                code_prefix=code,
                defaults={'name': name}
            )
            if created:
                print(f"Categoria criada: {name}")
        except Exception as e:
            print(f"Erro ao criar categoria {name}: {str(e)}")
            traceback.print_exc()

def create_products():
    print("\nCriando produtos...")
    products = [
        ('Arroz 5kg', 'AL', 25.90, 20.00),
        ('Feijão 1kg', 'AL', 8.90, 6.00),
        ('Coca-Cola 2L', 'BE', 8.50, 5.00),
        ('Guaraná 2L', 'BE', 7.50, 4.50),
        ('Detergente', 'LI', 2.90, 1.50),
        ('Sabão em Pó', 'LI', 15.90, 10.00),
        ('Shampoo', 'PE', 12.90, 8.00),
        ('Condicionador', 'PE', 12.90, 8.00),
        ('Caderno', 'PA', 15.90, 10.00),
        ('Caneta', 'PA', 2.90, 1.50),
    ]
    
    for name, category_code, sale_price, cost_price in products:
        try:
            category = Category.objects.get(code_prefix=category_code)
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'sale_price': sale_price,
                    'cost_price': cost_price,
                    'stock_quantity': 1000,  # Aumentando o estoque inicial
                    'min_stock': 20,
                    'supplier': 'Fornecedor Teste'
                }
            )
            if created:
                print(f"Produto criado: {name}")
            else:
                # Atualizar estoque do produto existente
                product.stock_quantity = 1000
                product.save()
                print(f"Estoque do produto {name} atualizado")
        except Exception as e:
            print(f"Erro ao criar produto {name}: {str(e)}")
            traceback.print_exc()

def create_clients():
    print("\nCriando clientes...")
    clients = [
        ('João Silva', '123.456.789-00', '(11) 99999-9999'),
        ('Maria Santos', '987.654.321-00', '(11) 98888-8888'),
        ('Pedro Oliveira', '456.789.123-00', '(11) 97777-7777'),
        ('Ana Costa', '789.123.456-00', '(11) 96666-6666'),
        ('Carlos Pereira', '321.654.987-00', '(11) 95555-5555'),
    ]
    
    for i, (name, cpf, phone) in enumerate(clients, 1):
        try:
            client, created = Client.objects.get_or_create(
                code=f'CL{i:03d}',
                defaults={
                    'name': name,
                    'cpf_cnpj': cpf,
                    'phone': phone,
                    'credit_limit': 1000.00
                }
            )
            if created:
                print(f"Cliente criado: {name}")
        except Exception as e:
            print(f"Erro ao criar cliente {name}: {str(e)}")
            traceback.print_exc()

def create_sales():
    print("\nCriando vendas...")
    clients = list(Client.objects.all())
    products = list(Product.objects.all())
    
    if not clients:
        print("Nenhum cliente encontrado!")
        return
    
    if not products:
        print("Nenhum produto encontrado!")
        return
    
    # Criar vendas para os últimos 60 dias
    for i in range(60):
        date = timezone.now() - timedelta(days=i)
        
        # Criar 1-3 vendas por dia
        for _ in range(random.randint(1, 3)):
            try:
                with transaction.atomic():
                    client = random.choice(clients)
                    sale = Sale.objects.create(
                        code=f'V{date.strftime("%Y%m%d")}{random.randint(1000, 9999)}',
                        client=client,
                        date=date,
                        total_amount=0,
                        payment_method=random.choice(['dinheiro', 'cartao', 'pix']),
                        status='pago'
                    )
                    
                    # Adicionar 1-5 itens por venda
                    total_amount = 0
                    num_items = random.randint(1, 5)
                    selected_products = random.sample(products, num_items)
                    
                    for product in selected_products:
                        # Verificar estoque disponível
                        max_quantity = min(5, product.stock_quantity)
                        if max_quantity > 0:
                            quantity = random.randint(1, max_quantity)
                            unit_price = product.sale_price
                            total_price = unit_price * quantity
                            
                            SaleItem.objects.create(
                                sale=sale,
                                product=product,
                                quantity=quantity,
                                unit_price=unit_price,
                                total_price=total_price
                            )
                            
                            total_amount += total_price
                            
                            # Atualizar estoque
                            product.stock_quantity -= quantity
                            product.save()
                    
                    if total_amount > 0:
                        sale.total_amount = total_amount
                        sale.save()
                        if i % 10 == 0:  # Mostrar progresso a cada 10 dias
                            print(f"Criada venda para o dia {date.strftime('%d/%m/%Y')}")
                    else:
                        sale.delete()
                        print(f"Venda cancelada por falta de estoque - dia {date.strftime('%d/%m/%Y')}")
                        
            except Exception as e:
                print(f"Erro ao criar venda: {str(e)}")
                traceback.print_exc()

def main():
    try:
        create_categories()
        create_products()
        create_clients()
        create_sales()
        print("\nDados de teste criados com sucesso!")
    except Exception as e:
        print(f"\nErro ao criar dados de teste: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    main() 