from django.urls import path
from .views import create_rate, list_rates, update_rate, delete_rate, get_rate

urlpatterns = [
    path('create/', create_rate, name='create-rate'),
    path('rates/', list_rates, name='all-rates'),
    path('<int:pk>/', get_rate, name='get-rate'),
    path('<int:pk>/update/', update_rate, name='update-rate'),
    path('<int:pk>/delete/', delete_rate, name='delete-rate'),
]