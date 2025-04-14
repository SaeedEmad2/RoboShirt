# designs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DesignViewSet

router = DefaultRouter()
router.register('uploads', DesignViewSet, basename='design')

urlpatterns = [
    path('', include(router.urls)),
]