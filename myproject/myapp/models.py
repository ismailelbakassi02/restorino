from django.db import models
from django.contrib.auth.models import AbstractUser

# -------------------------------
# Custom User Model
# -------------------------------

class User(AbstractUser):
    name = models.CharField(max_length=100)
    userType = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        swappable = 'AUTH_USER_MODEL'



# -------------------------------
# Admin
# -------------------------------
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

# -------------------------------
# Restaurant Owner
# -------------------------------
class RestaurantOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contactNumber = models.CharField(max_length=20)
    verificationStatus = models.CharField(max_length=50)

# -------------------------------
# Tourist
# -------------------------------
class Tourist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)

# -------------------------------
# Restaurant
# -------------------------------
class Restaurant(models.Model):
    owner = models.ForeignKey(RestaurantOwner, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    openTime = models.TimeField()
    closeTime = models.TimeField()
    hasAlcohol = models.BooleanField(default=False)
    description = models.TextField()
    profilePhoto = models.ImageField(upload_to='restaurant_photos/')
    contactNumber = models.CharField(max_length=20)
    createDate = models.DateTimeField(auto_now_add=True)
    averageRating = models.FloatField(default=0.0)

# -------------------------------
# Review
# -------------------------------
class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    tourist = models.ForeignKey(Tourist, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

# -------------------------------
# Menu Item
# -------------------------------
class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    photo = models.ImageField(upload_to='menu_photos/')

# -------------------------------
# Menu Item Review
# -------------------------------
class MenuItemReview(models.Model):
    menuItem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    tourist = models.ForeignKey(Tourist, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

# -------------------------------
# Ingredient
# -------------------------------
class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    menuItem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)

# -------------------------------
# Photo
# -------------------------------
class Photo(models.Model):
    imageUrl = models.ImageField(upload_to='uploads/')
    caption = models.CharField(max_length=255)
    uploadedBy = models.ForeignKey(User, on_delete=models.CASCADE)
    uploadDate = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50)
