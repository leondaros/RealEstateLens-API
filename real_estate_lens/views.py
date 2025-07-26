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
from real_estate_lens.utils.osm_utils import fetch_osm_pois

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
        filters = [
            {"key": "amenity", "values": ["school", "college", "university"]}
        ]
        try:
            pois = fetch_osm_pois(location.geometry.geojson, filters, verify=True) # (verify=True para produção)
            return Response(pois)
        except Exception as e:
            return Response({"error": "Erro ao consultar Overpass API", "details": str(e)}, status=503)

    @action(detail=True, methods=['get'])
    def leisure(self, request, pk=None):
        location = self.get_object()
        filters = [
            {"key": "leisure", "values": [
                "park", "playground", "sports_centre", "pitch", 
                "stadium", "recreation_ground", "dog_park"
            ]},
            {"key": "natural", "values": ["beach"]},
            {"key": "tourism", "values": ["picnic_site", "viewpoint", "zoo"]}
        ]
        try:
            pois = fetch_osm_pois(location.geometry.geojson, filters, verify=True) # (verify=True para produção)
            return Response(pois)
        except Exception as e:
            return Response({"error": "Erro ao consultar Overpass API", "details": str(e)}, status=503)    

    @action(detail=True, methods=['get'])
    def mobility(self, request, pk=None):
        location = self.get_object()
        filters = [
            {"key": "amenity", "values": ["bus_station", "taxi"]},
            {"key": "public_transport", "values": ["station", "platform"]}
        ]
        try:
            pois = fetch_osm_pois(location.geometry.geojson, filters, verify=True) # (verify=True para produção)
            return Response(pois)
        except Exception as e:
            return Response({"error": "Erro ao consultar Overpass API", "details": str(e)}, status=503)    

    @action(detail=True, methods=['get'])
    def commerce(self, request, pk=None):
        location = self.get_object()
        filters = [
            {"key": "shop", "values": [
                # Food & beverages
                "supermarket", "convenience", "bakery", "butcher", "greengrocer", "alcohol",
                "beverages", "cheese", "chocolate", "ice_cream", "seafood", "tea", "coffee", "deli", "pastry",
                # General store, department store, mall, variety, gift, craft, kiosk
                "general", "department_store", "mall", "variety_store", "gift", "craft", "kiosk",
                # Clothing, shoes, accessories
                "clothes", "shoes", "boutique", "accessories", "jewelry", "watch", "bag",
                # Other
                "stationery"
            ]},
            {"key": "amenity", "values": [
                "restaurant", "ice_cream", "fast_food", "cafe", "bar", "food_court",
                "bank", "atm", "post_office", "hairdresser", "laundry", "charging_station"
            ]}
        ]


        try:
            pois = fetch_osm_pois(location.geometry.geojson, filters, verify=True) # (verify=True para produção)
            return Response(pois)
        except Exception as e:
            return Response({"error": "Erro ao consultar Overpass API", "details": str(e)}, status=503)    

    @action(detail=True, methods=['get'])
    def health(self, request, pk=None):
        location = self.get_object()
        filters = [
            {"key": "amenity", "values": [
                "hospital",
                "clinic",
                "pharmacy",
                "doctors",
                "dentist",
                "laboratory",
                "healthcare",
                "nursing_home",
                "physiotherapist",
                "veterinary"
            ]}
        ]
        try:
            pois = fetch_osm_pois(location.geometry.geojson, filters, verify=True)
            return Response(pois)
        except Exception as e:
            return Response({"error": "Erro ao consultar Overpass API", "details": str(e)}, status=503)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer