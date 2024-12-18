from crypt import methods

from rest_framework.decorators import action
from real_estate_lens.models import User,Property,Location
from real_estate_lens.serializers import (UserSerializer,
    LocationSerializer, PropertySerializer, LocationPropertiesSerializer,
    LocationDetailsSerializer)
from rest_framework import viewsets, generics
from django.db.models import Avg, Prefetch
from rest_framework.response import Response
from rest_framework import status

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    @action(detail=False, methods=['get'])
    def average_price(self, request):
        """
        Endpoint customizado para calcular a média de preços.
        """
        media=self.queryset.aggregate(Avg("price", default=0))
        return Response(media, status=status.HTTP_200_OK)

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.prefetch_related(
        'properties',  # Propriedades relacionadas diretamente à Location
        Prefetch('sub_locations', queryset=Location.objects.prefetch_related('properties'))
    )
    serializer_class = LocationSerializer

    @action(detail=True, methods=['get'], url_path='properties', url_name='properties')
    def list_properties(self, request, pk=None):
        location = self.get_object()  # Get the current location instance
        serializer = LocationPropertiesSerializer(location)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='sub_locations', url_name='sub_locations')
    def sub_locations(self, request, pk=None):
        location = self.get_object()  # Get the current location instance
        serializer = LocationDetailsSerializer(location)
        return Response(serializer.data)