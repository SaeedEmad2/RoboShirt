from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RegisterView

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),  # Include all router URLs
    path('auth/register/', RegisterView.as_view(), name='register'),  # RegisterView path
]