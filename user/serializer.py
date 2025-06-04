from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserAddress, OTP

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'phone_number')
        read_only_fields = ('password',)

class UserUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True) 

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'email']
    
    def update(self, instance, validated_data):
        phone_number = validated_data.get('phone_number', instance.phone_number)
        if phone_number != instance.phone_number:
            if User.objects.filter(phone_number=phone_number).exists():
                raise serializers.ValidationError({"phone_number": "This phone number is already taken."})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserAddressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'street', 'location',  'main']

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['id', 'key', 'code', 'created_at', 'updated_at']
        read_only_fields = ['key', 'code', 'created_at', 'updated_at']