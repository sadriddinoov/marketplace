from rest_framework import serializers
from .models import RateModel

class RateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateModel
        fields = ['id', 'product', 'market', 'user', 'message', 'rate', 'anonym', 'created_at', 'updated_at']
        extra_kwargs = {
            'product': {'required': False, 'allow_null': True},
            'market': {'required': False, 'allow_null': True},
        }
        read_only_fields = ['user', 'created_at', 'updated_at']