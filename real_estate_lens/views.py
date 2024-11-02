from real_estate_lens.models import User,Property,Location
from real_estate_lens.serializers import UserSerializer, LocationSerializer, PropertySerializer
from rest_framework import viewsets

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = PropertySerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LocationSerializer