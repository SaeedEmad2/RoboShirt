from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RegisterView, LogoutView,UserDetailView

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),  # Include all router URLs
    path('auth/register/', RegisterView.as_view(), name='register'), 
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/user/', UserDetailView.as_view(), name='user_detail'),
    # RegisterView path
]