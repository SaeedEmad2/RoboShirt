from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from store.views import LogoutView, UserDetailView
from designs.views import GenerateImageView  # Import the GenerateImageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('store/', include('store.urls')),
    path('api/designs/', include('designs.urls')),  # Include designs router

    # Endpoint for generating designs
    path('api/designs/generate/', GenerateImageView.as_view(), name='generate-design'),

    # JWT Authentication Endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/user/', UserDetailView.as_view(), name='user_detail'),
]

# Add this at the end of the urlpatterns list
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)