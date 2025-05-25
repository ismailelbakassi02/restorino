from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User  # your custom user model


# ✅ Home page (requires login)
@login_required
def home_view(request):
    return render(request, 'home.html')


# ✅ Login view
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')  # redirects to / after login
            else:
                messages.error(request, 'Invalid password.')
        except User.DoesNotExist:
            messages.error(request, 'User with that email does not exist.')

    return render(request, 'login.html')


# ✅ Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ✅ Tourist signup
def tourist_signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        country = request.POST.get('country')
        gender = request.POST.get('gender')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(
                username=email,  # use email as username
                email=email,
                password=password,
                name=name,
                userType='tourist'
            )
            # You could also save country/gender if part of model
            login(request, user)
            return redirect('home')

    return render(request, 'tourist_signup.html')


# ✅ Owner signup
def owner_signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact = request.POST.get('contact')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                name=name,
                userType='owner'
            )
            # Optionally save contact if part of the model
            login(request, user)
            return redirect('home')

    return render(request, 'owner_signup.html')
