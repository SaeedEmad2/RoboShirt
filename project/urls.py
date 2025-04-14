from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from store import views
from store.urls import router
from designs.urls import router as designs_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('', include(router.urls)),
    path('', include(designs_router.urls)),
]


# Add this at the end of the urlpatterns list
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)