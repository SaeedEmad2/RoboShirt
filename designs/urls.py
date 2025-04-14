from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DesignViewSet ,TemplateViewSet



from .views import TemplateViewSet
router = DefaultRouter()
router.register('uploads', DesignViewSet, basename='design')

urlpatterns = [
    path('', include(router.urls)),
]


# Router for templates
router = DefaultRouter()
router.register('templates', TemplateViewSet, basename='template')

urlpatterns = [
    path('api/', include(router.urls)),  # Templates API
]