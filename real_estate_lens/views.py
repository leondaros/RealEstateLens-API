from crypt import methods

from rest_framework.decorators import action
from real_estate_lens.models import User,Property,Location, FavoriteLocation
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

    @action(detail=True,methods=['post'],url_path='toggle-favorite',url_name='toggle-favorite')
    def toggle_favorite(self, request, pk=None):
        """
        POST /users/{user_id}/toggle-favorite/
        Body: { "location_id": <id> }
        -> cria ou remove o favorite para essa location.
        """
        user = self.get_object()
        location_id = request.data.get('location_id')
        if not location_id:
            return Response(
                {"detail": "É preciso enviar 'location_id' no body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            loc = Location.objects.get(pk=location_id)
        except Location.DoesNotExist:
            return Response(
                {"detail": "Location não encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        fav_qs = FavoriteLocation.objects.filter(user=user, location=loc)
        if fav_qs.exists():
            # já era favorito → desfavorita
            fav_qs.delete()
            serializer = UserSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            # não era favorito → cria
            FavoriteLocation.objects.create(user=user, location=loc)
            serializer = UserSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )


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

    @action(detail=True, methods=['get'], url_path='details', url_name='details')
    def details(self, request, pk=None):
        location = self.get_object()  # Get the current location instance
        serializer = LocationDetailsSerializer(location)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='search', url_name='search')
    def search(self, request):
        """
        Search locations by name containing the given string.
        String must be at least 3 characters long.
        """
        search_term = request.query_params.get('q', '')
        if len(search_term) < 3:
            return Response(
                {"error": "Search term must be at least 3 characters long"},
                status=status.HTTP_400_BAD_REQUEST
            )

        locations = Location.objects.filter(name__icontains=search_term)
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)