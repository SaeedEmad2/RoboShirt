from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,CartViewSet
from . import views


router = DefaultRouter()
router.register('products',views.ProductViewSet, basename='product')
router.register('carts',views.CartViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
