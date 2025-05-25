# myapp/views.py
from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html')

def tourist_signup_view(request):
    return render(request, 'tourist_signup.html')

def owner_signup_view(request):
    return render(request, 'owner_signup.html')

