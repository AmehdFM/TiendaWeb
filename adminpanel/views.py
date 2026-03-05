from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from store.models import Product, Tag, Transaction
from django.contrib import messages

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
    total_stock = Product.objects.aggregate(total=Sum('stock'))['total'] or 0
    
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
            stock=stock,
            image_url_1=img1,
            image_url_2=img2,
            image_url_3=img3,
            image_url_4=img4
        )
        product.tags.set(tag_ids)
        
        # Initial restock transaction
        if int(stock) > 0:
            Transaction.objects.create(
                product=product,
                type='RESTOCK',
                quantity=stock
            )
            
        messages.success(request, 'Producto agregado correctamente.')
        return redirect('adminpanel:product_list')
        
    tags = Tag.objects.all()
    return render(request, 'adminpanel/product_form.html', {'tags': tags})

def update_stock(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Can be standard 'change' (-1, 1) or specific 'quantity' with 'type'
        change = int(request.POST.get('change', 0))
        qty = int(request.POST.get('quantity', 0))
        t_type = request.POST.get('type') # 'SALE', 'RESTOCK'
        
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
            product.stock += final_change
            product.save()
            
            Transaction.objects.create(
                product=product,
                type=t_type,
                quantity=final_change
            )
            messages.success(request, f'Inventario actualizado para {product.name}.')
            
    return redirect('adminpanel:product_list')

from django.http import JsonResponse

def product_detail_json(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': float(product.price),
        'stock': product.stock,
        'image_url_1': product.image_url_1,
        'image_url_2': product.image_url_2,
        'image_url_3': product.image_url_3,
        'image_url_4': product.image_url_4,
        'tags': list(product.tags.values_list('id', flat=True))
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

