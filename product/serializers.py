from rest_framework import serializers
from market.serializers import MarketModelSerializer
from .models import ProductModel

class ProductModelSerializer(serializers.ModelSerializer):
    market = MarketModelSerializer(read_only=True)
    rate = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = ['id', 'name', 'description', 'category', 'price', 'discount', 'market', 'available', 'rate']
    
    def get_rate(self, obj):
        if getattr(obj, 'rate', None) is None:
            return "Hali baxolanmagan"
        return round(obj.rate, 1)