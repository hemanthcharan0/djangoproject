from django.shortcuts import render, get_object_or_404, redirect
from mainapp.models import Product, Category
from .models import Order, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
import json

# Replace your current user_dashboard function with this:
@login_required
def user_dashboard(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.all()

    if query:
        products = products.filter(Q(title__icontains=query) | Q(category__name__icontains=query))
    
    if category_id:
        products = products.filter(category_id=category_id)

    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)

    categories = Category.objects.all()
    orders = Order.objects.filter(user=request.user).order_by('-date')
    
    # CRITICAL CHANGE: Changed 'userdashboard.html' to 'userdashborad.html'
    return render(request, 'userdashborad.html', {
        'products': products, 
        'orders': orders, 
        'categories': categories
    })

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        
        return JsonResponse({
            'status': 'success', 
            'quantity': cart_item.quantity,
            'cart_count': cart.items.count()
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        items = []
        total_price = 0
        for item in cart.items.all():
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'title': item.product.title,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'total': float(item.get_total_price()),
                'image_url': item.product.image.url
            })
            total_price += item.get_total_price()
            
        return JsonResponse({'status': 'success', 'items': items, 'total_price': float(total_price)})
    except Cart.DoesNotExist:
        return JsonResponse({'status': 'success', 'items': [], 'total_price': 0})

@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        # Logic to handle product_id or item_id for dashboard compatibility
        if 'product_id' in data:
            cart = Cart.objects.get(user=request.user)
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=data['product_id'])
        else:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                return JsonResponse({'status': 'success', 'quantity': 0})
        
        cart_item.save()
        return JsonResponse({'status': 'success', 'quantity': cart_item.quantity})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)
        orders_created = []
        for item in cart.items.all():
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                price=item.get_total_price(),
                status='Pending'
            )
        cart.items.all().delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)