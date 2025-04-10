from django.contrib import admin
from django.urls import path, include
from store import views
from store.urls import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('', include(router.urls)),
]