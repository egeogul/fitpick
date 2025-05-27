from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


CATEGORY_CHOICES = [
    ('topwear', 'Top Wear'),
    ('bottomwear', 'Bottom Wear'),
    ('shoes', 'Shoes'),
    ('accessories', 'Accessories'),
]

# store/models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(default="No description provided.")
    image = models.ImageField(upload_to='product_images/')
    image_alt = models.ImageField(upload_to='product_images/', blank=True, null=True)
    CATEGORY_CHOICES = (
        ('Topwear', 'Topwear'),
        ('Bottomwear', 'Bottomwear'),
        ('Shoes', 'Shoes'),
        ('Accessories', 'Accessories'),
    )
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default="Topwear")

    def __str__(self):
        return self.name



class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # ✅ Add this line

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)