from django.urls import path
from .views import create_product, list_products, get_product, update_product, delete_product

urlpatterns = [
    path('create/', create_product, name='product-create'),
    path('products/', list_products, name='product-list'),
    path('<int:pk>/', get_product, name='product-detail'),
    path('<int:pk>/update/', update_product, name='product-update'),
    path('<int:pk>/delete/', delete_product, name='product-delete'),
]
