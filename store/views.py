# Django imports
from django.shortcuts import render

# DRF imports
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework import mixins

import uuid
import random
# Local imports
from .models import Product, Cart, CartItem,Payment, Order
from .serializers import (
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
    RegisterSerializer,
    LogoutSerializer,
    PaymentSerializer, 
    PaymentInitiateSerializer, 
    PaymentVerifySerializer,
    PaymentReceiptSerializer
)


# Product ViewSet
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product_size', 'product_color']  # Filter by these fields
    search_fields = ['product_name']  # Search by product name
    ordering_fields = ['product_price']  # Order by price


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    permission_classes = [AllowAny]
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects \
            .filter(cart_id=self.kwargs['cart_pk']) \
            .select_related('product')



class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": serializer.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=200)
        return Response(serializer.errors, status=400)
    
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=200)
        return Response({"error": "Refresh token is required or invalid."}, status=400)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }, status=status.HTTP_200_OK)
    


class PaymentViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='initiate')
    def initiate_payment(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            payment_method = serializer.validated_data['payment_method']
            
            # Get the order
            order = Order.objects.get(id=order_id)
            
            # Check that the order belongs to the user
            if order.user != request.user:
                return Response(
                    {"error": "You don't have permission to pay for this order"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate a unique transaction ID
            transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            
            # Create a masked card detail if using credit card
            card_details = None
            if payment_method == 'credit_card':
                card_number = serializer.validated_data.get('card_number')
                card_details = {
                    'card_number': f"XXXX-XXXX-XXXX-{card_number[-4:]}",
                    'expiry': f"{serializer.validated_data.get('expiry_month')}/{serializer.validated_data.get('expiry_year')}"
                }
            
            # Create payment record with 'processing' status
            payment = Payment.objects.create(
                payment_method=payment_method,
                order=order,
                user=request.user,
                status='processing',
                amount=order.total_price,
                transaction_id=transaction_id,
                card_details=card_details
            )
            
            # Simulate payment processing (for mock API)
            # Simulate success 80% of the time, failure 20%
            success = random.random() < 0.8
            
            if success:
                # Generate a receipt ID
                receipt_id = f"RCPT-{uuid.uuid4().hex[:10].upper()}"
                
                # Update payment status and add receipt
                payment.status = 'completed'
                payment.receipt_id = receipt_id
                payment.save()
                
                # Update order status
                order.status = 'processing'
                order.save()
                
                return Response({
                    "status": "success",
                    "message": "Payment processed successfully",
                    "transaction_id": transaction_id,
                    "receipt_id": receipt_id
                }, status=status.HTTP_200_OK)
            else:
                # Simulate payment failure
                payment.status = 'failed'
                payment.save()
                
                return Response({
                    "status": "failed",
                    "message": "Payment failed. Please try again.",
                    "transaction_id": transaction_id,
                    "error_code": "CARD_DECLINED"  # Simulate an error code
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='verify')
    def verify_payment(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        if serializer.is_valid():
            transaction_id = serializer.validated_data['transaction_id']
            
            try:
                payment = Payment.objects.get(transaction_id=transaction_id, user=request.user)
                
                return Response({
                    "status": payment.status,
                    "message": f"Payment status: {payment.status}",
                    "transaction_id": transaction_id,
                    "receipt_id": payment.receipt_id if payment.status == 'completed' else None
                }, status=status.HTTP_200_OK)
                
            except Payment.DoesNotExist:
                return Response({
                    "error": "Transaction not found"
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentReceiptView(RetrieveAPIView):
    serializer_class = PaymentReceiptSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'receipt_id'
    
    def get_queryset(self):
        return Payment.objects.filter(
            user=self.request.user, 
            status='completed'
        )