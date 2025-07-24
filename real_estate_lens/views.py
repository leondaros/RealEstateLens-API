from rest_framework.decorators import action
from real_estate_lens.models import Property,Location, FavoriteLocation
from real_estate_lens.serializers import (UserRegisterSerializer, UserSerializer,
    LocationSerializer, PropertySerializer, LocationPropertiesSerializer,
    LocationDetailsSerializer)
from rest_framework import viewsets, generics
from django.db.models import Avg, Prefetch
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from real_estate_lens.serializers import CustomTokenObtainPairSerializer
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
import requests


User = get_user_model()

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

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

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
    
    @action(detail=True, methods=['get'])
    def schools(self, request, pk=None):
        location = self.get_object()
        import json
        from shapely.geometry import shape, Point

        polygon_geojson = location.geometry.geojson
        polygon = shape(json.loads(polygon_geojson))

        minx, miny, maxx, maxy = polygon.bounds

        query = f"""
        [out:json][timeout:25];
        (
        node["amenity"="school"]({miny},{minx},{maxy},{maxx});
        way["amenity"="school"]({miny},{minx},{maxy},{maxx});
        relation["amenity"="school"]({miny},{minx},{maxy},{maxx});
        );
        out center;
        """
        overpass_url = "https://overpass-api.de/api/interpreter"
        try:
            response = requests.post(overpass_url, data=query, timeout=30,verify=False)
            response.raise_for_status()
            data = response.json().get("elements", [])
        except Exception as e:
            return Response({"error": "Erro ao consultar Overpass API", "details": str(e)}, status=503)

        schools = []
        for el in data:
            if "lat" in el and "lon" in el:
                pt = Point(el["lon"], el["lat"])
            elif "center" in el:
                pt = Point(el["center"]["lon"], el["center"]["lat"])
            else:
                continue
            if polygon.contains(pt):
                schools.append({
                    "name": el.get("tags", {}).get("name"),
                    "lat": pt.y,
                    "lon": pt.x
                })

        return Response(data)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer