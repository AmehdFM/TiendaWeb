from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Tag, Transaction, ProductSize, PhysicalStore

def home(request, tag_slug=None):
    products = Product.objects.all()
    tag = None
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags=tag)
        
    context = {
        'products': products,
        'current_tag': tag,
    }
    return render(request, 'store/home.html', context)

def store_locations(request):
    stores = PhysicalStore.objects.filter(is_active=True).order_by('name')
    return render(request, 'store/stores.html', {'stores': stores})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Related products: items with at least one common tag, excluding current product
    related_products = Product.objects.filter(tags__in=product.tags.all()).exclude(id=product.id).distinct()[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'sizes': product.sizes.all().order_by('name'),
    }
    return render(request, 'store/product_detail.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size_id = request.POST.get('size_id')
    
    if not size_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Debe seleccionar una talla.'}, status=400)
        messages.error(request, 'Por favor, selecciona una talla.')
        return redirect('store:product_detail', product_id=product_id)

    size = get_object_or_404(ProductSize, id=size_id, product=product)

    if size.stock <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Talla agotada.'}, status=400)
        messages.error(request, 'Lo sentimos, esta talla está agotada.')
        return redirect('store:product_detail', product_id=product_id)

    cart = request.session.get('cart', {})
    
    # Store size_id as string since session keys must be strings
    size_id_str = str(size_id)
    if size_id_str in cart:
        cart[size_id_str] += 1
    else:
        cart[size_id_str] = 1
        
    request.session['cart'] = cart
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': len(cart)})
        
    messages.success(request, f'"{product.name}" (Talla {size.name}) agregado al carrito.')
    return redirect('store:cart')

from django.http import JsonResponse

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for size_id_str, quantity in cart.items():
        try:
            size = ProductSize.objects.get(id=int(size_id_str))
            product = size.product
            item_total = product.price * quantity
            total_price += item_total
            cart_items.append({
                'product': product,
                'size': size,
                'quantity': quantity,
                'item_total': item_total,
            })
        except ProductSize.DoesNotExist:
            pass # Size was deleted
            
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'store/cart.html', context)

def clear_cart(request):
    request.session['cart'] = {}
    return redirect('store:cart')

def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.warning(request, 'El carrito está vacío.')
            return redirect('store:home')
            
        for size_id_str, quantity in cart.items():
            try:
                size = ProductSize.objects.get(id=int(size_id_str))
                product = size.product
                
                # Check sufficient stock
                if size.stock < quantity:
                    messages.error(request, f'No hay suficiente stock para {product.name} en talla {size.name}.')
                    return redirect('store:cart')

                # Reduce stock of specific size
                size.stock -= quantity
                size.save()
                
                # Create transaction linked to product and size
                Transaction.objects.create(
                    product=product,
                    product_size=size,
                    type='SALE',
                    quantity=-quantity # Negative for sales
                )
            except ProductSize.DoesNotExist:
                pass
                
        request.session['cart'] = {}
        messages.success(request, '¡Gracias por su compra! El stock ha sido actualizado por talla.')
        return redirect('store:home')
        
    return redirect('store:cart')
