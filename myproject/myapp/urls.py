from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/tourist/', views.tourist_signup_view, name='signup_tourist'),
    path('signup/owner/', views.owner_signup_view, name='signup_owner'),
]
