import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_control.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Category, Product, Client, Sale, SaleItem, StockMovement, Payment

def create_superuser():
    """Create a superuser if it doesn't exist"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser created: admin / admin123")
    else:
        print("Superuser already exists")

def create_categories():
    """Create sample product categories"""
    categories = [
        "Alimentos",
        "Bebidas",
        "Limpeza",
        "Higiene Pessoal",
        "Papelaria",
        "Eletrônicos",
        "Ferramentas",
        "Utilidades Domésticas"
    ]
    
    created_categories = []
    for i, name in enumerate(categories):
        category, created = Category.objects.get_or_create(name=name)
        created_categories.append(category)
        if created:
            print(f"Category created: {name}")
        else:
            print(f"Category already exists: {name}")
    
    return created_categories

def create_products(categories):
    """Create sample products for each category"""
    products_data = {
        "Alimentos": [
            ("A001", "Arroz 5kg", "Arroz tipo 1", Decimal("25.90"), Decimal("18.50"), 50, 10),
            ("A002", "Feijão 1kg", "Feijão carioca", Decimal("8.90"), Decimal("6.20"), 40, 8),
            ("A003", "Açúcar 5kg", "Açúcar refinado", Decimal("15.90"), Decimal("12.30"), 30, 5),
            ("A004", "Café 500g", "Café torrado e moído", Decimal("12.50"), Decimal("9.80"), 25, 5),
            ("A005", "Macarrão 500g", "Macarrão espaguete", Decimal("4.50"), Decimal("3.20"), 60, 12),
        ],
        "Bebidas": [
            ("B001", "Refrigerante 2L", "Refrigerante cola", Decimal("8.90"), Decimal("6.50"), 40, 8),
            ("B002", "Suco 1L", "Suco de laranja", Decimal("5.90"), Decimal("4.20"), 30, 6),
            ("B003", "Água Mineral 500ml", "Água sem gás", Decimal("2.50"), Decimal("1.80"), 100, 20),
            ("B004", "Cerveja 350ml", "Cerveja pilsen", Decimal("4.90"), Decimal("3.50"), 60, 12),
            ("B005", "Vinho 750ml", "Vinho tinto seco", Decimal("35.90"), Decimal("28.50"), 15, 3),
        ],
        "Limpeza": [
            ("L001", "Detergente 500ml", "Detergente líquido", Decimal("3.50"), Decimal("2.30"), 50, 10),
            ("L002", "Sabão em Pó 1kg", "Sabão em pó multiuso", Decimal("12.90"), Decimal("9.80"), 30, 6),
            ("L003", "Desinfetante 1L", "Desinfetante perfumado", Decimal("8.90"), Decimal("6.50"), 40, 8),
            ("L004", "Água Sanitária 1L", "Água sanitária", Decimal("4.50"), Decimal("3.20"), 45, 9),
            ("L005", "Esponja", "Esponja dupla face", Decimal("2.90"), Decimal("1.80"), 60, 12),
        ],
        "Higiene Pessoal": [
            ("H001", "Sabonete", "Sabonete perfumado", Decimal("2.90"), Decimal("1.80"), 80, 16),
            ("H002", "Shampoo 350ml", "Shampoo para todos os tipos de cabelo", Decimal("12.90"), Decimal("9.50"), 30, 6),
            ("H003", "Creme Dental 90g", "Creme dental com flúor", Decimal("4.50"), Decimal("3.20"), 50, 10),
            ("H004", "Papel Higiênico 4un", "Papel higiênico folha dupla", Decimal("8.90"), Decimal("6.50"), 40, 8),
            ("H005", "Desodorante Roll-on", "Desodorante antitranspirante", Decimal("9.90"), Decimal("7.50"), 35, 7),
        ],
        "Papelaria": [
            ("P001", "Caderno 96 folhas", "Caderno espiral", Decimal("12.90"), Decimal("9.50"), 25, 5),
            ("P002", "Caneta Esferográfica", "Caneta azul", Decimal("1.90"), Decimal("1.20"), 100, 20),
            ("P003", "Lápis", "Lápis preto nº 2", Decimal("1.50"), Decimal("0.90"), 80, 16),
            ("P004", "Borracha", "Borracha branca", Decimal("2.50"), Decimal("1.50"), 60, 12),
            ("P005", "Apontador", "Apontador com depósito", Decimal("3.90"), Decimal("2.50"), 40, 8),
        ],
        "Eletrônicos": [
            ("E001", "Pilha AA 4un", "Pilha alcalina", Decimal("12.90"), Decimal("9.50"), 30, 6),
            ("E002", "Carregador USB", "Carregador para celular", Decimal("25.90"), Decimal("18.50"), 15, 3),
            ("E003", "Fone de Ouvido", "Fone de ouvido com fio", Decimal("19.90"), Decimal("14.50"), 20, 4),
            ("E004", "Cabo USB", "Cabo USB tipo C", Decimal("15.90"), Decimal("11.50"), 25, 5),
            ("E005", "Adaptador", "Adaptador de tomada", Decimal("8.90"), Decimal("6.50"), 30, 6),
        ],
        "Ferramentas": [
            ("F001", "Martelo", "Martelo de unha", Decimal("29.90"), Decimal("22.50"), 10, 2),
            ("F002", "Chave de Fenda", "Chave de fenda média", Decimal("12.90"), Decimal("9.50"), 15, 3),
            ("F003", "Alicate", "Alicate universal", Decimal("25.90"), Decimal("19.50"), 12, 2),
            ("F004", "Fita Métrica", "Fita métrica 5m", Decimal("15.90"), Decimal("11.50"), 20, 4),
            ("F005", "Parafuso 100un", "Parafusos sortidos", Decimal("8.90"), Decimal("6.50"), 30, 6),
        ],
        "Utilidades Domésticas": [
            ("U001", "Prato", "Prato de porcelana", Decimal("12.90"), Decimal("9.50"), 20, 4),
            ("U002", "Copo 6un", "Conjunto de copos de vidro", Decimal("25.90"), Decimal("19.50"), 15, 3),
            ("U003", "Panela", "Panela de alumínio", Decimal("45.90"), Decimal("35.50"), 10, 2),
            ("U004", "Toalha", "Toalha de banho", Decimal("29.90"), Decimal("22.50"), 20, 4),
            ("U005", "Lixeira", "Lixeira plástica 15L", Decimal("19.90"), Decimal("14.50"), 15, 3),
        ],
    }
    
    created_products = []
    for category in categories:
        if category.name in products_data:
            for code, name, description, sale_price, cost_price, stock, min_stock in products_data[category.name]:
                product, created = Product.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'description': description,
                        'category': category,
                        'sale_price': sale_price,
                        'cost_price': cost_price,
                        'stock_quantity': stock,
                        'min_stock': min_stock,
                        'supplier': f"Fornecedor {category.name}"
                    }
                )
                
                created_products.append(product)
                
                # Create initial stock movement if product was just created
                if created:
                    StockMovement.objects.create(
                        product=product,
                        quantity=stock,
                        movement_type='entrada',
                        reason='Estoque inicial'
                    )
                    print(f"Product created: {name} ({code})")
                else:
                    print(f"Product already exists: {name} ({code})")
    
    return created_products

def create_clients():
    """Create sample clients"""
    clients_data = [
        ("C001", "João Silva", "123.456.789-00", "(11) 98765-4321", "Rua A, 123", "joao@email.com", Decimal("500.00")),
        ("C002", "Maria Oliveira", "987.654.321-00", "(11) 91234-5678", "Rua B, 456", "maria@email.com", Decimal("1000.00")),
        ("C003", "Pedro Santos", "456.789.123-00", "(11) 92345-6789", "Rua C, 789", "pedro@email.com", Decimal("800.00")),
        ("C004", "Ana Souza", "789.123.456-00", "(11) 93456-7890", "Rua D, 012", "ana@email.com", Decimal("1200.00")),
        ("C005", "Carlos Ferreira", "321.654.987-00", "(11) 94567-8901", "Rua E, 345", "carlos@email.com", Decimal("600.00")),
        ("C006", "Fernanda Lima", "654.987.321-00", "(11) 95678-9012", "Rua F, 678", "fernanda@email.com", Decimal("900.00")),
        ("C007", "Ricardo Alves", "789.321.654-00", "(11) 96789-0123", "Rua G, 901", "ricardo@email.com", Decimal("700.00")),
        ("C008", "Juliana Costa", "321.987.654-00", "(11) 97890-1234", "Rua H, 234", "juliana@email.com", Decimal("1500.00")),
        ("C009", "Marcelo Dias", "654.321.987-00", "(11) 98901-2345", "Rua I, 567", "marcelo@email.com", Decimal("1100.00")),
        ("C010", "Patrícia Rocha", "987.654.321-00", "(11) 99012-3456", "Rua J, 890", "patricia@email.com", Decimal("800.00")),
    ]
    
    created_clients = []
    for code, name, cpf_cnpj, phone, address, email, credit_limit in clients_data:
        client, created = Client.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'cpf_cnpj': cpf_cnpj,
                'phone': phone,
                'address': address,
                'email': email,
                'credit_limit': credit_limit
            }
        )
        
        created_clients.append(client)
        
        if created:
            print(f"Client created: {name} ({code})")
        else:
            print(f"Client already exists: {name} ({code})")
    
    return created_clients

def create_sales(clients, products):
    """Create sample sales with items"""
    # Payment methods and statuses
    payment_methods = ['dinheiro', 'cartao', 'pix', 'prazo']
    statuses = ['pago', 'pendente']
    
    # Create sales for the last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    created_sales = []
    sale_code_counter = 1
    
    # Create 50 random sales
    for _ in range(50):
        # Random date within the last 30 days
        sale_date = start_date + timedelta(days=random.randint(0, 30), 
                                          hours=random.randint(8, 20),
                                          minutes=random.randint(0, 59))
        
        # Random client (sometimes None for "consumer final")
        client = random.choice(clients) if random.random() > 0.2 else None
        
        # Random payment method
        payment_method = random.choice(payment_methods)
        
        # Status based on payment method
        if payment_method == 'prazo':
            status = 'pendente'
            # Ensure client is not None for sales on credit
            if client is None:
                client = random.choice(clients)
        else:
            status = random.choice(statuses)
            if status == 'pendente':
                payment_method = 'prazo'  # Force prazo for pending sales
                # Ensure client is not None for pending sales
                if client is None:
                    client = random.choice(clients)
        
        # Create sale
        sale_code = f"V{sale_code_counter:04d}"
        sale_code_counter += 1
        
        sale = Sale.objects.create(
            code=sale_code,
            client=client,
            date=sale_date,
            payment_method=payment_method,
            status=status,
            notes=f"Venda de teste {sale_code}"
        )
        
        # Add 1-5 random products to the sale
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, num_items)
        
        for product in selected_products:
            # Random quantity between 1 and 3
            quantity = random.randint(1, 3)
            
            # Sometimes apply a small discount
            unit_price = product.sale_price
            if random.random() > 0.7:
                discount = random.uniform(0.05, 0.15)
                unit_price = unit_price * Decimal(1 - discount)
            
            # Create sale item
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=unit_price
            )
        
        # For paid sales with a client, create payment
        if status == 'pago' and client is not None:
            Payment.objects.create(
                client=client,
                sale=sale,
                amount=sale.total_amount,
                payment_date=sale_date,
                notes=f"Pagamento da venda {sale_code}"
            )
        # For some pending sales, create partial payments
        elif status == 'pendente' and client is not None and random.random() > 0.5:
            payment_percentage = random.uniform(0.3, 0.7)
            payment_amount = sale.total_amount * Decimal(payment_percentage)
            
            Payment.objects.create(
                client=client,
                sale=sale,
                amount=payment_amount,
                payment_date=sale_date,
                notes=f"Pagamento parcial da venda {sale_code}"
            )
        
        created_sales.append(sale)
        print(f"Sale created: {sale_code} - {sale_date.strftime('%d/%m/%Y')} - R$ {sale.total_amount}")
    
    return created_sales

def create_stock_movements(products):
    """Create additional stock movements"""
    movement_types = ['entrada', 'saida', 'ajuste']
    reasons = [
        'Compra de fornecedor',
        'Devolução de cliente',
        'Ajuste de inventário',
        'Produto danificado',
        'Transferência entre lojas'
    ]
    
    # Create 30 random stock movements
    for _ in range(30):
        product = random.choice(products)
        movement_type = random.choice(movement_types)
        
        # Determine quantity based on movement type
        if movement_type == 'entrada':
            quantity = random.randint(5, 20)
        elif movement_type == 'saida':
            quantity = min(random.randint(1, 5), product.stock_quantity)
            if quantity == 0:
                quantity = 1  # Ensure at least 1 for outgoing
        else:  # ajuste
            quantity = random.randint(-3, 5)
        
        # Skip if trying to remove more than available
        if movement_type == 'saida' and quantity > product.stock_quantity:
            continue
        
        # Create movement
        StockMovement.objects.create(
            product=product,
            quantity=quantity,
            movement_type=movement_type,
            reason=random.choice(reasons),
            date=timezone.now() - timedelta(days=random.randint(0, 30))
        )
        
        print(f"Stock movement created: {product.name} - {movement_type} - {quantity}")

def main():
    """Main function to populate the database"""
    print("Starting database population...")
    
    # Create superuser
    create_superuser()
    
    # Create categories
    categories = create_categories()
    
    # Create products
    products = create_products(categories)
    
    # Create clients
    clients = create_clients()
    
    # Create sales and sale items
    sales = create_sales(clients, products)
    
    # Create additional stock movements
    create_stock_movements(products)
    
    print("Database population completed!")

if __name__ == "__main__":
    main()