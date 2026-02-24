from django.shortcuts import render, redirect, get_object_or_404
from mainapp.models import Product, Category
from django.contrib.auth.models import User
from userapp.models import Order

def admin_dashboard(request):
    orders = Order.objects.all().order_by('-date')
    return render(request, 'admindashboard.html', {'orders': orders})

def admin_login(request):
    return render(request, 'adminlogin.html')

def products(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category') # Get category from form

        Product.objects.create(
            image=image,
            title=title,
            description=description,
            price=price,
            category_id=category_id
        )
        return redirect('products')

    products = Product.objects.all()
    categories = Category.objects.all() # Fetch categories for the modal
    return render(request, 'products.html', {'products': products, 'categories': categories})

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.title = request.POST.get('title')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.category_id = request.POST.get('category')
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        
        product.save()
        return redirect('products')
    return redirect('products')

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('products')
    return redirect('products')

def view_users(request):
    users = User.objects.all()
    return render(request, 'view_users.html', {'users': users})