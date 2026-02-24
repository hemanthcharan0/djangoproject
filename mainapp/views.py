from django.shortcuts import render, redirect
from .models import Product
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

# Create your views here.

def index(request):
    return render(request, 'index.html')

def navbar(request):
    return render(request, 'navbar.html')

def footer(request):
    return render(request, 'footer.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            auth_login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match")
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
             messages.error(request, "Username already exists")
             return redirect('register')

        if User.objects.filter(email=email).exists():
             messages.error(request, "Email already exists")
             return redirect('register')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.save()

        # Send Welcome Email
        subject = "Welcome to Truedge!"
        message = f"""Hi {username},\n\nThank you for registering at Truedge. We are absolutely thrilled to have you on board!
        \n\nExplore our latest collections and exclusive deals customized just for you.
        \n\nIf you have any questions, feel free to reply to this email.
        \n\nBest Regards,
        \n\nTruedge Team"""
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            print(f"Error sending email: {e}")

        messages.success(request, "Your account has been successfully created. Please login.")
        return redirect('login')

    return render(request, 'register.html') 

def collections(request):
    products = Product.objects.all()
    return render(request, 'collections.html', {'products': products})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')