from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Tag, Transaction

def home(request, tag_slug=None):
    tags = Tag.objects.all()
    products = Product.objects.all()
    tag = None
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags=tag)
        
    context = {
        'tags': tags,
        'products': products,
        'current_tag': tag,
    }
    return render(request, 'store/home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Related products: items with at least one common tag, excluding current product
    related_products = Product.objects.filter(tags__in=product.tags.all()).exclude(id=product.id).distinct()[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    # Store ID as string since session keys must be strings
    pid_str = str(product_id)
    if pid_str in cart:
        cart[pid_str] += 1
    else:
        cart[pid_str] = 1
        
    request.session['cart'] = cart
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': len(cart)})
        
    messages.success(request, f'"{product.name}" agregado al carrito.')
    return redirect('store:cart')

from django.http import JsonResponse

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for pid_str, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(pid_str))
            item_total = product.price * quantity
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            pass # Product was deleted
            
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
            
        for pid_str, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(pid_str))
                # Reduce stock
                product.stock -= quantity
                product.save()
                
                # Create transaction
                Transaction.objects.create(
                    product=product,
                    type='SALE',
                    quantity=-quantity # Negative for sales
                )
            except Product.DoesNotExist:
                pass
                
        request.session['cart'] = {}
        messages.success(request, '¡Gracias por su compra (simulada)! Las transacciones han sido registradas.')
        return redirect('store:home')
        
    return redirect('store:cart')
