import os
import django
import random
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Tag, Product, Transaction

def generate_demo_data():
    print("Iniciando generación de datos demo...")

    # 1. Limpiar datos existentes (opcional para demo limpia)
    Transaction.objects.all().delete()
    Product.objects.all().delete()
    Tag.objects.all().delete()

    # 2. Crear Etiquetas
    tags_data = [
        {'name': 'Casual', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/3534/3534312.png'},
        {'name': 'Elegante', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/3531/3531818.png'},
        {'name': 'Deportivo', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/4163/4163673.png'},
        {'name': 'Accesorios', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/3050/3050239.png'},
    ]
    
    tags = {}
    for t in tags_data:
        tag, created = Tag.objects.get_or_create(name=t['name'], defaults={'icon_url': t['icon_url']})
        tags[t['name']] = tag
        print(f"Etiqueta creada: {tag.name}")

    # 3. Datos de Productos
    products_data = [
        {
            'name': 'Camiseta Minimalista Blanca',
            'description': 'Camiseta de algodón 100% orgánico con corte moderno y tacto suave. Ideal para uso diario.',
            'price': Decimal('25.00'),
            'stock': 45,
            'image_url_1': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&q=80&w=800',
            'tags': ['Casual']
        },
        {
            'name': 'Sudadera "Slate" con Capucha',
            'description': 'Sudadera premium en color gris asfalto. Tejido pesado de alta calidad para máxima comodidad.',
            'price': Decimal('49.99'),
            'stock': 20,
            'image_url_1': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&q=80&w=800',
            'tags': ['Casual', 'Deportivo']
        },
        {
            'name': 'Pantalón Chino Beige Slim',
            'description': 'Pantalón versátil con corte ajustado. Perfecto para combinar con camisas o camisetas.',
            'price': Decimal('55.00'),
            'stock': 15,
            'image_url_1': 'https://images.unsplash.com/photo-1473966968600-fa804b86829b?auto=format&fit=crop&q=80&w=800',
            'tags': ['Elegante', 'Casual']
        },
        {
            'name': 'Reloj Industrial Silver',
            'description': 'Reloj con diseño minimalista, correa de cuero negra y esfera de acero inoxidable.',
            'price': Decimal('120.00'),
            'stock': 10,
            'image_url_1': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=800',
            'tags': ['Accesorios', 'Elegante']
        },
        {
            'name': 'Chaqueta Técnica Impermeable',
            'description': 'Protección total contra el viento y la lluvia con un diseño urbano sofisticado.',
            'price': Decimal('89.00'),
            'stock': 8,
            'image_url_1': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&q=80&w=800',
            'tags': ['Deportivo', 'Casual']
        },
        {
            'name': 'Zapatillas "Urban Walk"',
            'description': 'Calzado ligero con suela ergonómica. Diseñadas para caminar largas distancias por la ciudad.',
            'price': Decimal('75.00'),
            'stock': 25,
            'image_url_1': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&q=80&w=800',
            'tags': ['Deportivo', 'Casual']
        }
    ]

    created_products = []
    for p in products_data:
        prod = Product.objects.create(
            name=p['name'],
            description=p['description'],
            price=p['price'],
            stock=p['stock'],
            image_url_1=p['image_url_1']
        )
        for t_name in p['tags']:
            prod.tags.add(tags[t_name])
        created_products.append(prod)
        print(f"Producto creado: {prod.name}")

    # 4. Generar Transacciones Iniciales
    print("Generando transacciones históricas...")
    now = timezone.now()
    
    # Simular algunos Restocks (Entradas)
    for prod in created_products:
        Transaction.objects.create(
            product=prod,
            type='RESTOCK',
            quantity=prod.stock + random.randint(5, 10),
            date=now - timedelta(days=random.randint(5, 15))
        )

    # Simular algunas Ventas (Salidas)
    for i in range(15):
        prod = random.choice(created_products)
        qty = random.randint(1, 3)
        Transaction.objects.create(
            product=prod,
            type='SALE',
            quantity=-qty,
            date=now - timedelta(days=random.randint(0, 4), hours=random.randint(0, 23))
        )

    print("\n¡Demo data generada con éxito!")

if __name__ == "__main__":
    generate_demo_data()
