from django.contrib import admin
from .models import Customer,  Product, Cart, CartItem, Order, Shipment, Payment

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Shipment)
admin.site.register(Payment)