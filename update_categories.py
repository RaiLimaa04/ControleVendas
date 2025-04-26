import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_control.settings')
django.setup()

from store.models import Category

def update_category_prefixes():
    # Dicionário de prefixos por categoria
    prefixes = {
        'Limpeza': 'LP',
        'Bebidas': 'BB',
        'Alimentos': 'AL',
        'Higiene': 'HG',
        'Eletrônicos': 'EL',
        'Vestuário': 'VT',
        'Outros': 'OT'
    }
    
    # Atualiza cada categoria
    for category in Category.objects.all():
        # Gera um prefixo baseado no nome da categoria
        prefix = prefixes.get(category.name, category.name[:2].upper())
        
        # Verifica se o prefixo já existe
        while Category.objects.filter(code_prefix=prefix).exists():
            # Se existir, adiciona um número
            prefix = f"{prefix}1"
        
        category.code_prefix = prefix
        category.save()
        print(f"Categoria '{category.name}' atualizada com prefixo '{prefix}'")

if __name__ == '__main__':
    update_category_prefixes() 