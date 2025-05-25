# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/tourist/', views.tourist_signup_view, name='tourist_signup'),
    path('signup/owner/', views.owner_signup_view, name='owner_signup'),
]
