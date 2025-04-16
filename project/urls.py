from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from store.urls import router as store_router
from designs.urls import router as designs_router
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from store.views import LogoutView  # Import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('api/', include(store_router.urls)),  # Include store router
    path('api/designs/', include(designs_router.urls)),  # Include designs router
    path('api/', include('store.urls')),  # Include store URLs directly under /api/
    
    # JWT Authentication Endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),  # Add logout endpoint
]

# Add this at the end of the urlpatterns list
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)