from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Product, Cart
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product_size', 'product_color']  # Filter by these fields
    search_fields = ['product_name']  # Search by product name
    ordering_fields = ['product_price']  # Order by price
    
    







