from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Design, Template
from .serializers import DesignSerializer, TemplateSerializer
from store.models import Customer

class DesignViewSet(viewsets.ModelViewSet):
    serializer_class = DesignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return designs only for the logged-in user
        try:
            customer = Customer.objects.get(user=self.request.user)
            return Design.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            return Design.objects.none()
    
    def perform_create(self, serializer):
        # Automatically set the customer based on the logged-in user
        try:
            customer = Customer.objects.get(user=self.request.user)
            serializer.save(customer=customer)
        except Customer.DoesNotExist:
            raise ValidationError("User does not have an associated customer account")
    
    @action(detail=True, methods=['delete'], url_path='delete')
    def custom_delete(self, request, pk=None):
        design = self.get_object()
        design.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class TemplateViewSet(ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Allow filtering by category
    filterset_fields = ['category']  # Filter by category field
    
    # Allow searching by category name
    search_fields = ['category']  # Search by category name