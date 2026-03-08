import os
import django
import random
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Tag, Product, Transaction, ProductSize

def generate_demo_data():
    print("Iniciando generación de datos demo...")

    # 1. Limpiar datos existentes (opcional para demo limpia)
    Transaction.objects.all().delete()
    ProductSize.objects.all().delete()
    Product.objects.all().delete()
    Tag.objects.all().delete()

    # 2. Crear Etiquetas
    tags_data = [
        {'name': 'Casual', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/3534/3534312.png'},
        {'name': 'Elegante', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/3531/3531818.png'},
        {'name': 'Deportivo', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/4163/4163673.png'},
        {'name': 'Accesorios', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/3050/3050239.png'},
        {'name': 'Zapatos', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/2872/2872581.png'},
        {'name': 'Joyería', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/1154/1154674.png'},
        {'name': 'Bolsos', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/3133/3133615.png'},
        {'name': 'Gafas de Sol', 'icon_url': 'https://cdn-icons-png.flaticon.com/512/1039/1039860.png'},
    ]
    
    tags = {}
    for t in tags_data:
        tag, created = Tag.objects.get_or_create(name=t['name'], defaults={'icon_url': t['icon_url']})
        tags[t['name']] = tag
        print(f"Etiqueta creada: {tag.name}")

    # 3. Datos de Productos
    clothing_sizes = ['S', 'M', 'L', 'XL']
    shoe_sizes = ['40', '41', '42', '43', '44']
    universal_size = ['Única']

    products_data = [
        {
            'name': 'Camiseta Minimalista Blanca',
            'description': 'Camiseta de algodón 100% orgánico con corte moderno y tacto suave. Ideal para uso diario.',
            'price': Decimal('25.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&q=80&w=800',
            'tags': ['Casual'],
            'sizes': clothing_sizes
        },
        {
            'name': 'Sudadera "Slate" con Capucha',
            'description': 'Sudadera premium en color gris asfalto. Tejido pesado de alta calidad para máxima comodidad.',
            'price': Decimal('49.99'),
            'image_url_1': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&q=80&w=800',
            'tags': ['Casual', 'Deportivo'],
            'sizes': clothing_sizes
        },
        {
            'name': 'Pantalón Chino Beige Slim',
            'description': 'Pantalón versátil con corte ajustado. Perfecto para combinar con camisas o camisetas.',
            'price': Decimal('55.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1473966968600-fa804b86829b?auto=format&fit=crop&q=80&w=800',
            'tags': ['Elegante', 'Casual'],
            'sizes': clothing_sizes
        },
        {
            'name': 'Reloj Industrial Silver',
            'description': 'Reloj con diseño minimalista, correa de cuero negra y esfera de acero inoxidable.',
            'price': Decimal('120.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=800',
            'tags': ['Accesorios', 'Elegante'],
            'sizes': universal_size
        },
        {
            'name': 'Chaqueta Técnica Impermeable',
            'description': 'Protección total contra el viento y la lluvia con un diseño urbano sofisticado.',
            'price': Decimal('89.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&q=80&w=800',
            'tags': ['Deportivo', 'Casual'],
            'sizes': clothing_sizes
        },
        {
            'name': 'Zapatillas "Urban Walk"',
            'description': 'Calzado ligero con suela ergonómica. Diseñadas para caminar largas distancias por la ciudad.',
            'price': Decimal('75.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&q=80&w=800',
            'tags': ['Deportivo', 'Casual', 'Zapatos'],
            'sizes': shoe_sizes
        },
        {
            'name': 'Sneakers Blancos Clásicos',
            'description': 'Zapatillas de cuero sintético premium. Un básico atemporal para cualquier outfit casual.',
            'price': Decimal('65.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&q=80&w=800',
            'tags': ['Zapatos', 'Casual'],
            'sizes': shoe_sizes
        },
        {
            'name': 'Botas Chelsea de Cuero',
            'description': 'Botas de cuero genuino con paneles elásticos. Elegancia y comodidad en cada paso.',
            'price': Decimal('95.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1638247025967-b4e38f787b76?auto=format&fit=crop&q=80&w=800',
            'tags': ['Zapatos', 'Elegante'],
            'sizes': shoe_sizes
        },
        {
            'name': 'Reloj Cronógrafo de Lujo',
            'description': 'Reloj de precisión con brazalete de acero y esfera azul medianoche. Resistente al agua.',
            'price': Decimal('180.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?auto=format&fit=crop&q=80&w=800',
            'tags': ['Accesorios', 'Elegante', 'Joyería'],
            'sizes': universal_size
        },
        {
            'name': 'Gafas de Sol Aviador Classic',
            'description': 'Icónico diseño de aviador con montura dorada y lentes polarizadas.',
            'price': Decimal('45.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?auto=format&fit=crop&q=80&w=800',
            'tags': ['Accesorios', 'Gafas de Sol'],
            'sizes': universal_size
        },
        {
            'name': 'Mochila de Lona Urbana',
            'description': 'Mochila resistente con compartimento para portátil. Perfecta para el explorador urbano.',
            'price': Decimal('60.00'),
            'image_url_1': 'https://images.unsplash.com/photo-1553062407-98eeb94c6a62?auto=format&fit=crop&q=80&w=800',
            'tags': ['Accesorios', 'Bolsos', 'Casual'],
            'sizes': universal_size
        }
    ]

    created_sizes = []
    for p in products_data:
        prod = Product.objects.create(
            name=p['name'],
            description=p['description'],
            price=p['price'],
            image_url_1=p['image_url_1']
        )
        for t_name in p['tags']:
            prod.tags.add(tags[t_name])
        
        # Crear tallas con stock aleatorio
        for s_name in p['sizes']:
            stock = random.randint(5, 20)
            psize = ProductSize.objects.create(
                product=prod,
                name=s_name,
                stock=stock
            )
            created_sizes.append(psize)
            
        print(f"Producto creado: {prod.name} ({len(p['sizes'])} tallas)")

    # 4. Generar Transacciones Iniciales
    print("Generando transacciones históricas...")
    now = timezone.now()
    
    # Simular algunos Restocks (Entradas)
    for psize in created_sizes:
        Transaction.objects.create(
            product=psize.product,
            product_size=psize,
            type='RESTOCK',
            quantity=psize.stock + random.randint(5, 10),
            date=now - timedelta(days=random.randint(5, 15))
        )

    # Simular algunas Ventas (Salidas)
    for i in range(30):
        psize = random.choice(created_sizes)
        qty = random.randint(1, 2)
        Transaction.objects.create(
            product=psize.product,
            product_size=psize,
            type='SALE',
            quantity=-qty,
            date=now - timedelta(days=random.randint(0, 4), hours=random.randint(0, 23))
        )

    print("\n¡Demo data generada con éxito!")

    print("\n¡Demo data generada con éxito!")

if __name__ == "__main__":
    generate_demo_data()
