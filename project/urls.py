from django.contrib import admin
from django.urls import path, include
from store.urls import router as store_router  # Rename the store router
from designs.urls import router as designs_router  # Rename the designs router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('api/', include(store_router.urls)),  # Include store router
    path('api/designs/', include(designs_router.urls)),  # Include designs router
]