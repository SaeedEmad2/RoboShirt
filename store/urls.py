from django.urls import path, include
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CartViewSet, CartItemViewSet, RegisterView, LogoutView, UserDetailView

# Main router
router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('carts', CartViewSet, basename='carts')

# Nested router for cart items
carts_router = NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-items')

# Combine all URLs
urlpatterns = [
    path('', include(router.urls)),  # Include main router URLs
    path('', include(carts_router.urls)),  # Include nested router URLs
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/user/', UserDetailView.as_view(), name='user_detail'),
]