from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RegisterView, LogoutView

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),  # Include all router URLs
    path('auth/register/', RegisterView.as_view(), name='register'), 
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    # RegisterView path
]