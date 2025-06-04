from rest_framework import serializers
from .models import MarketModel

class MarketModelSerializer(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField()
    class Meta:
        model = MarketModel
        fields = ['id', 'name', 'description', 'location', 'rate']
        
    def get_rate(self, obj):
        if getattr(obj, 'rate', None) is None:
            return "Hali baxolanmagan"
        return round(obj.rate, 1)