from django.contrib import admin
from .models import OrderModel, OrderItemModel

admin.site.register(OrderModel)
admin.site.register(OrderItemModel)

# Register your models here.
