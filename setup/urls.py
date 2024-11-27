from django.contrib import admin
from django.urls import path,include
from real_estate_lens.views import UserViewSet, LocationViewSet, PropertyViewSet, ListPropertiesLocation
from rest_framework import routers

router = routers.DefaultRouter()
router.register('users',UserViewSet,basename='Users')
router.register('properties',PropertyViewSet,basename='Properties')
router.register('locations',LocationViewSet,basename='Locations')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(router.urls)),
]
