from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from store.urls import router as store_router
from designs.urls import router as designs_router
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from store.views import LogoutView, UserDetailView # Import LogoutView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from store import views
from store.urls import router
from designs.urls import router as designs_router
from store.urls import router as store_router  # Rename the store router
from designs.urls import router as designs_router  # Rename the designs router
# Import the router from designs app
urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('', include(router.urls)),
    path('', include(designs_router.urls)),
    path('store/', include('store.urls')),
    
    path('api/designs/', include(designs_router.urls)),  # Include designs router
    path('', include(designs_router.urls)),
    
    # JWT Authentication Endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'), 
    path('api/auth/user/', UserDetailView.as_view(), name='user_detail'),# Add logout endpoint
]

# Add this at the end of the urlpatterns list
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)