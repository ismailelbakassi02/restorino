from django import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class TouristRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2', 'country', 'gender']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.userType = 'tourist'
        if commit:
            user.save()
        return user

class OwnerRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2', 'contact']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.userType = 'owner'
        if commit:
            user.save()
        return user
