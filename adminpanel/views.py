from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from store.models import (
    Product, Tag, Transaction, ProductSize,
    WholesaleClient, WholesalePurchase,
    PhysicalStore, StoreInventory,
)
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal


def dashboard(request):
    # Metrics
    last_30_days = timezone.now() - timedelta(days=30)

    products_sold_30 = Transaction.objects.filter(
        type='SALE',
        date__gte=last_30_days
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # quantity is negative for sales in my logic, let's make it positive for display
    products_sold_30 = abs(products_sold_30)

    total_sales_count = Transaction.objects.filter(type='SALE').count()

    products_added_30 = Product.objects.filter(created_at__gte=last_30_days).count()

    total_products = Product.objects.count()
    total_stock = ProductSize.objects.aggregate(total=Sum('stock'))['total'] or 0

    # Recent transactions
    recent_transactions = Transaction.objects.all().order_by('-date')[:10]

    context = {
        'products_sold_30': products_sold_30,
        'total_sales_count': total_sales_count,
        'products_added_30': products_added_30,
        'total_products': total_products,
        'total_stock': total_stock,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'adminpanel/dashboard.html', context)


def product_list(request):
    query = request.GET.get('q')
    tag_id = request.GET.get('tag')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if tag_id:
        products = products.filter(tags__id=tag_id)

    tags = Tag.objects.all()
    tags_data = []
    for t in tags:
        tags_data.append({
            'id': t.id,
            'name': t.name,
            'is_selected': str(t.id) == tag_id
        })

    context = {
        'products': products,
        'tags': tags_data,
        'tags_full': tags,  # Added for the modal
    }
    return render(request, 'adminpanel/product_list.html', context)


def product_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        img1 = request.POST.get('image_url_1')
        img2 = request.POST.get('image_url_2')
        img3 = request.POST.get('image_url_3')
        img4 = request.POST.get('image_url_4')
        tag_ids = request.POST.getlist('tags')

        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            image_url_1=img1,
            image_url_2=img2,
            image_url_3=img3,
            image_url_4=img4
        )
        product.tags.set(tag_ids)

        # We don't have default sizes here yet in the simple form,
        # but we could add a default 'Única' size if we want.
        ProductSize.objects.create(product=product, name='Única', stock=stock or 0)

        messages.success(request, 'Producto agregado correctamente con talla Única.')
        return redirect('adminpanel:product_list')

    tags = Tag.objects.all()
    return render(request, 'adminpanel/product_form.html', {'tags': tags})


def update_stock(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        size_id = request.POST.get('size_id')

        if not size_id:
            messages.error(request, 'Debe seleccionar una talla.')
            return redirect('adminpanel:product_list')

        size = get_object_or_404(ProductSize, id=size_id, product=product)

        # Can be standard 'change' (-1, 1) or specific 'quantity' with 'type'
        change = int(request.POST.get('change', 0))
        qty = int(request.POST.get('quantity', 0))
        t_type = request.POST.get('type')  # 'SALE', 'RESTOCK'

        final_change = 0
        if change != 0:
            final_change = change
            t_type = 'RESTOCK' if change > 0 else 'ADJUSTMENT'
        elif qty != 0 and t_type:
            if t_type == 'SALE':
                final_change = -abs(qty)
            elif t_type == 'RESTOCK':
                final_change = abs(qty)
            else:
                final_change = qty

        if final_change != 0:
            size.stock += final_change
            size.save()

            Transaction.objects.create(
                product=product,
                product_size=size,
                type=t_type,
                quantity=final_change
            )
            messages.success(request, f'Inventario actualizado para {product.name} (Talla: {size.name}).')

    return redirect('adminpanel:product_list')


def product_detail_json(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': float(product.price),
        'total_stock': product.total_stock,
        'image_url_1': product.image_url_1,
        'image_url_2': product.image_url_2,
        'image_url_3': product.image_url_3,
        'image_url_4': product.image_url_4,
        'tags': list(product.tags.values_list('id', flat=True)),
        'sizes': list(product.sizes.values('id', 'name', 'stock'))
    }
    return JsonResponse(data)


def product_edit(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        # We don't update stock directly here, use transactions
        product.image_url_1 = request.POST.get('image_url_1')
        product.image_url_2 = request.POST.get('image_url_2')
        product.image_url_3 = request.POST.get('image_url_3')
        product.image_url_4 = request.POST.get('image_url_4')
        product.save()

        tag_ids = request.POST.getlist('tags')
        product.tags.set(tag_ids)

        messages.success(request, f'Producto "{product.name}" actualizado correctamente.')
        return redirect('adminpanel:product_list')
    return redirect('adminpanel:product_list')


def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'adminpanel/tag_list.html', {'tags': tags})


def tag_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        icon_url = request.POST.get('icon_url')
        Tag.objects.create(name=name, icon_url=icon_url)
        messages.success(request, 'Etiqueta agregada correctamente.')
        return redirect('adminpanel:tag_list')

    return render(request, 'adminpanel/tag_form.html')


def tag_detail_json(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    data = {
        'id': tag.id,
        'name': tag.name,
        'icon_url': tag.icon_url,
        'slug': tag.slug
    }
    return JsonResponse(data)


def tag_edit(request, tag_id):
    if request.method == 'POST':
        tag = get_object_or_404(Tag, id=tag_id)
        tag.name = request.POST.get('name')
        tag.icon_url = request.POST.get('icon_url')
        tag.save()
        messages.success(request, f'Etiqueta "{tag.name}" actualizada correctamente.')
    return redirect('adminpanel:tag_list')


def operation_list(request):
    tag_id = request.GET.get('tag')
    op_type = request.GET.get('type')
    month = request.GET.get('month')
    year = request.GET.get('year')
    query = request.GET.get('q')

    transactions = Transaction.objects.all().order_by('-date')

    if tag_id:
        transactions = transactions.filter(product__tags__id=tag_id)
    if op_type:
        transactions = transactions.filter(type=op_type)
    if month:
        transactions = transactions.filter(date__month=month)
    if year:
        transactions = transactions.filter(date__year=year)
    if query:
        transactions = transactions.filter(product__name__icontains=query)

    tags = Tag.objects.all()
    tags_data = []
    for t in tags:
        tags_data.append({
            'id': t.id,
            'name': t.name,
            'is_selected': str(t.id) == tag_id
        })

    types = Transaction.TRANSACTION_TYPES
    types_data = []
    for val, label in types:
        types_data.append({
            'value': val,
            'label': label,
            'is_selected': val == op_type
        })

    # Get available years/months for the filter (distinct)
    years = Transaction.objects.dates('date', 'year', order='DESC')
    years_data = []
    for y in years:
        year_str = y.strftime('%Y')
        years_data.append({
            'value': year_str,
            'is_selected': year_str == year
        })

    months_list = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    months_data = []
    for num, name in months_list:
        months_data.append({
            'value': num,
            'name': name,
            'is_selected': str(num) == month
        })

    context = {
        'transactions': transactions,
        'tags': tags_data,
        'types': types_data,
        'months': months_data,
        'years': years_data,
        'current_q': query,
        'has_filters': any([tag_id, op_type, month, year, query])
    }
    return render(request, 'adminpanel/operation_list.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# CLIENTES MAYORISTAS
# ─────────────────────────────────────────────────────────────────────────────

def wholesale_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    clients = WholesaleClient.objects.all()

    if query:
        clients = clients.filter(name__icontains=query) | clients.filter(company__icontains=query)

    if status_filter == 'active':
        clients = clients.filter(is_active=True)
    elif status_filter == 'inactive':
        clients = clients.filter(is_active=False)

    context = {
        'clients': clients,
        'current_q': query,
        'current_status': status_filter,
        'is_status_active': status_filter == 'active',
        'is_status_inactive': status_filter == 'inactive',
    }
    return render(request, 'adminpanel/wholesale_list.html', context)


def wholesale_add(request):
    if request.method == 'POST':
        client = WholesaleClient.objects.create(
            name=request.POST.get('name'),
            company=request.POST.get('company', ''),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            notes=request.POST.get('notes', ''),
            is_active=request.POST.get('is_active') == 'on',
        )
        messages.success(request, f'Cliente mayorista "{client.name}" creado correctamente.')
        return redirect('adminpanel:wholesale_detail', client_id=client.id)
    return redirect('adminpanel:wholesale_list')


def wholesale_detail(request, client_id):
    client = get_object_or_404(WholesaleClient, id=client_id)
    purchases = client.purchases.select_related('product', 'product_size').order_by('-date')
    products = Product.objects.prefetch_related('sizes').order_by('name')

    context = {
        'client': client,
        'purchases': purchases,
        'products': products,
    }
    return render(request, 'adminpanel/wholesale_detail.html', context)


def wholesale_edit(request, client_id):
    if request.method == 'POST':
        client = get_object_or_404(WholesaleClient, id=client_id)
        client.name = request.POST.get('name')
        client.company = request.POST.get('company', '')
        client.phone = request.POST.get('phone', '')
        client.email = request.POST.get('email', '')
        client.address = request.POST.get('address', '')
        client.notes = request.POST.get('notes', '')
        client.is_active = request.POST.get('is_active') == 'on'
        client.save()
        messages.success(request, f'Cliente "{client.name}" actualizado.')
    return redirect('adminpanel:wholesale_detail', client_id=client_id)


def wholesale_detail_json(request, client_id):
    client = get_object_or_404(WholesaleClient, id=client_id)
    data = {
        'id': client.id,
        'name': client.name,
        'company': client.company,
        'phone': client.phone,
        'email': client.email,
        'address': client.address,
        'notes': client.notes,
        'is_active': client.is_active,
    }
    return JsonResponse(data)


def wholesale_purchase_add(request, client_id):
    if request.method == 'POST':
        client = get_object_or_404(WholesaleClient, id=client_id)
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size_id')
        quantity = int(request.POST.get('quantity', 1))
        unit_price = Decimal(request.POST.get('unit_price', '0'))
        notes = request.POST.get('notes', '')

        product = get_object_or_404(Product, id=product_id)
        size = get_object_or_404(ProductSize, id=size_id, product=product) if size_id else None

        WholesalePurchase.objects.create(
            client=client,
            product=product,
            product_size=size,
            quantity=quantity,
            unit_price=unit_price,
            notes=notes,
        )
        messages.success(request, f'Compra registrada para {client.name}.')
    return redirect('adminpanel:wholesale_detail', client_id=client_id)


def wholesale_sizes_json(request, product_id):
    """Endpoint helper: returns sizes for a given product (for the purchase modal)."""
    product = get_object_or_404(Product, id=product_id)
    sizes = list(product.sizes.values('id', 'name', 'stock'))
    return JsonResponse({'sizes': sizes, 'price': float(product.price)})


# ─────────────────────────────────────────────────────────────────────────────
# TIENDAS FÍSICAS
# ─────────────────────────────────────────────────────────────────────────────

def physical_store_list(request):
    query = request.GET.get('q', '')
    stores = PhysicalStore.objects.all()
    if query:
        stores = stores.filter(name__icontains=query) | stores.filter(city__icontains=query)
    context = {
        'stores': stores,
        'current_q': query,
    }
    return render(request, 'adminpanel/physical_store_list.html', context)


def physical_store_add(request):
    if request.method == 'POST':
        store = PhysicalStore.objects.create(
            name=request.POST.get('name'),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
            description=request.POST.get('description', ''),
            is_active=request.POST.get('is_active') == 'on',
        )
        messages.success(request, f'Tienda "{store.name}" creada correctamente.')
        return redirect('adminpanel:physical_store_detail', store_id=store.id)
    return redirect('adminpanel:physical_store_list')


def physical_store_detail(request, store_id):
    store = get_object_or_404(PhysicalStore, id=store_id)
    inventory = store.inventory.select_related('product', 'product_size').order_by('product__name', 'product_size__name')
    products = Product.objects.prefetch_related('sizes').order_by('name')

    context = {
        'store': store,
        'inventory': inventory,
        'products': products,
    }
    return render(request, 'adminpanel/physical_store_detail.html', context)


def physical_store_edit(request, store_id):
    if request.method == 'POST':
        store = get_object_or_404(PhysicalStore, id=store_id)
        store.name = request.POST.get('name')
        store.address = request.POST.get('address', '')
        store.city = request.POST.get('city', '')
        store.phone = request.POST.get('phone', '')
        store.email = request.POST.get('email', '')
        store.description = request.POST.get('description', '')
        store.is_active = request.POST.get('is_active') == 'on'
        store.save()
        messages.success(request, f'Tienda "{store.name}" actualizada.')
    return redirect('adminpanel:physical_store_detail', store_id=store_id)


def physical_store_detail_json(request, store_id):
    store = get_object_or_404(PhysicalStore, id=store_id)
    data = {
        'id': store.id,
        'name': store.name,
        'address': store.address,
        'city': store.city,
        'phone': store.phone,
        'email': store.email,
        'description': store.description,
        'is_active': store.is_active,
    }
    return JsonResponse(data)


def store_inventory_update(request, store_id):
    if request.method == 'POST':
        store = get_object_or_404(PhysicalStore, id=store_id)
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size_id')
        quantity = int(request.POST.get('quantity', 0))

        product = get_object_or_404(Product, id=product_id)
        size = get_object_or_404(ProductSize, id=size_id, product=product)

        inventory_item, created = StoreInventory.objects.get_or_create(
            store=store,
            product_size=size,
            defaults={'product': product, 'quantity': quantity}
        )
        if not created:
            inventory_item.quantity = quantity
            inventory_item.save()

        action = 'asignado' if created else 'actualizado'
        messages.success(request, f'Inventario {action}: {product.name} ({size.name}) — {quantity} uds.')
    return redirect('adminpanel:physical_store_detail', store_id=store_id)


def store_inventory_delete(request, store_id, inventory_id):
    if request.method == 'POST':
        item = get_object_or_404(StoreInventory, id=inventory_id, store_id=store_id)
        item.delete()
        messages.success(request, 'Asignación de inventario eliminada.')
    return redirect('adminpanel:physical_store_detail', store_id=store_id)

