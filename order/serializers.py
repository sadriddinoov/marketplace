from rest_framework import serializers
from .models import OrderModel, OrderItemModel
from product.serializers import ProductModelSerializer
from market.serializers import MarketModelSerializer
from user.serializer import UserAddressSerializer

class OrderItemModelSerializer(serializers.ModelSerializer):
    product = ProductModelSerializer(read_only=True)

    class Meta:
        model = OrderItemModel
        fields = ['id', 'product', 'quantity', 'created_at']

class OrderModelSerializer(serializers.ModelSerializer):
    product = ProductModelSerializer(read_only=True)
    market = MarketModelSerializer(read_only=True)
    user_address = UserAddressSerializer(read_only=True)
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = OrderModel
        fields = ['id', 'product', 'user', 'market', 'user_address', 'created_at', 'order_items']

    def get_order_items(self, obj):
        items = obj.orderitemmodel_set.all()
        return OrderItemModelSerializer(items, many=True).data
