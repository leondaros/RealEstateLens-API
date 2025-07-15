from django.contrib import admin
from django.urls import path,include
from real_estate_lens.views import CustomTokenObtainPairView, UserViewSet, LocationViewSet, PropertyViewSet, UserRegisterView
from rest_framework import routers
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register('users',UserViewSet,basename='Users')
router.register('properties',PropertyViewSet,basename='Properties')
router.register('locations',LocationViewSet,basename='Locations')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/register/', UserRegisterView.as_view(), name='user-register'),
    path('',include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]