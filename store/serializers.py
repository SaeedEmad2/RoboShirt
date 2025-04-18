from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Cart, CartItem,Payment, Order
from .models import Product, Cart
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

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


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']




class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_method', 'order', 'status', 'amount', 'payment_date', 'transaction_id', 'receipt_id']
        read_only_fields = ['transaction_id', 'receipt_id', 'status', 'payment_date']

class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_CHOICES)
    card_number = serializers.CharField(max_length=16, min_length=16, required=False)
    expiry_month = serializers.CharField(max_length=2, required=False)
    expiry_year = serializers.CharField(max_length=2, required=False)
    cvv = serializers.CharField(max_length=3, min_length=3, required=False)
    
    def validate(self, data):
        # Validate order exists
        order_id = data.get('order_id')
        payment_method = data.get('payment_method')
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError(f"Order with ID {order_id} does not exist")
        
        # If payment method is credit card, validate card details
        if payment_method == 'credit_card':
            required_fields = ['card_number', 'expiry_month', 'expiry_year', 'cvv']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(f"{field} is required for credit card payments")
        
        return data

class PaymentVerifySerializer(serializers.Serializer):
    transaction_id = serializers.CharField()

class PaymentReceiptSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    order_number = serializers.SerializerMethodField()
    
    def get_customer_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
    
    def get_order_number(self, obj):
        return obj.order.id
    
    class Meta:
        model = Payment
        fields = ['id', 'receipt_id', 'transaction_id', 'payment_method', 'amount', 
                  'payment_date', 'status', 'customer_name', 'order_number']