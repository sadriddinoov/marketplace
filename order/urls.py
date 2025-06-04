from django.urls import path
from .views import create_order, list_orders, order_detail, update_order, delete_order, delete_order_item,  update_order_item

urlpatterns = [
    path('create/', create_order),
    path('orders/', list_orders),
    path('<int:pk>/', order_detail),
    path('update/<int:pk>/', update_order),
    path('delete/<int:pk>/', delete_order),
    path('item/update/<int:pk>/', update_order_item),
    path('item/delete/<int:pk>/', delete_order_item),
]
