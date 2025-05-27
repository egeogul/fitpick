from django.contrib import admin
from .models import Product, Wishlist, CartItem, Order


admin.site.register(Wishlist)
admin.site.register(CartItem)
admin.site.register(Order)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    fields = ('name', 'price', 'description', 'category', 'image', 'image_alt')  # add image_alt here

admin.site.register(Product, ProductAdmin)