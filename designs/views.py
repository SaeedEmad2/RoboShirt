from rest_framework.viewsets import ModelViewSet
from .models import Template
from .serializers import TemplateSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class TemplateViewSet(ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Allow filtering by category
    filterset_fields = ['category']  # Filter by category field
    
    # Allow searching by category name
    search_fields = ['category']  # Search by category name