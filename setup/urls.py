from django.contrib import admin
from django.urls import path,include
from real_estate_lens.views import UserViewSet, LocationViewSet, PropertyViewSet
from rest_framework import routers
from django.conf import settings

router = routers.DefaultRouter()
router.register('users',UserViewSet,basename='Users')
router.register('properties',PropertyViewSet,basename='Properties')
router.register('locations',LocationViewSet,basename='Locations')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(router.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]