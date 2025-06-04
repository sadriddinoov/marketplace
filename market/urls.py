from django.urls import path
from .views import list_market, create_market, update_market, delete_market, market_detail

urlpatterns = [
    path('create/', create_market, name='create_market'),
    path('markets/', list_market, name='get_all_markets'),
    path('<int:pk>/', market_detail, name='market_detail'),
    path('<int:pk>/update/', update_market, name='update_market'),
    path('<int:pk>/delete/', delete_market, name='delete_market'),
]
