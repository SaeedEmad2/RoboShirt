from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet

# Router for templates
router = DefaultRouter()
router.register('templates', TemplateViewSet, basename='template')

urlpatterns = [
    path('api/', include(router.urls)),  # Templates API
]