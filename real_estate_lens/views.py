from crypt import methods

from rest_framework.decorators import action
from rest_framework.views import APIView

from real_estate_lens.models import User,Property,Location
from real_estate_lens.serializers import (UserSerializer,
    LocationSerializer, PropertySerializer, ListPropertiesLocationSerializer)
from rest_framework import viewsets, generics
from django.db.models import Avg
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
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @action(detail=True, methods=['get'], url_path='properties', url_name='properties')
    def list_properties(self, request, pk=None):
        """
        Lista todas as propriedades relacionadas a uma localização específica.
        """
        # Filtrar propriedades pela localização
        properties = Property.objects.filter(location_id=pk)

        # Serializar os dados
        serializer = PropertySerializer(properties, many=True)

        return Response(serializer.data, status=200)

class ListPropertiesLocation(generics.ListAPIView):
    def get_queryset(self):
        queryset=Property.objects.filter(location_id=self.kwargs['pk'])
        return queryset
    serializer_class = ListPropertiesLocationSerializer