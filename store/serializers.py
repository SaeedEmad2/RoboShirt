from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Cart
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirmation']

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirmation')  # Remove password_confirmation
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        refresh = attrs.get('refresh')
        try:
            RefreshToken(refresh)  # Validate the refresh token
        except Exception as e:
            raise serializers.ValidationError("Invalid or expired refresh token.")
        return attrs
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Product
        fields = '__all__'
        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id']
        
