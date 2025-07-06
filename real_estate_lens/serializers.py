from rest_framework import serializers
from real_estate_lens.models import User,Property,Location
from django.db.models import Avg
import locale

class UserSerializer(serializers.ModelSerializer):
    favorite_locations = serializers.SerializerMethodField()
    class Meta:
        model=User
        fields= ['id', 'name', 'email', 'role', 'favorite_locations']

    def get_favorite_locations(self, obj):
        return LocationSummarySerializer(obj.favorite_locations.all(), many=True).data

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model=Property
        fields= ['description', 'square_meters', 'bedrooms', 'bathrooms',
                 'price', 'link', 'listing_date', 'source', 'property_type',
                 'location', 'coordinates']

class LocationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        # apenas os campos que você quer expor
        fields = ['id', 'name', 'location_type']

class LocationSerializer(serializers.ModelSerializer):
    center = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField()
    class Meta:
        model=Location
        fields= ['id','name','location_type','geometry','average_price','center']

    def get_center(self, obj):
        centroid = obj.center()
        if centroid:
            return {'type': 'Point', 'coordinates': [centroid.y, centroid.x]}
        return None

class LocationPropertiesSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()
    center = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField()
    class Meta:
        model=Location
        fields=['id','name','location_type','geometry','average_price','center','properties']

    def get_properties(self, obj):
        # As propriedades já estão pré-carregadas com prefetch_related
        properties = obj.properties.all()
        return PropertySerializer(properties, many=True).data

    def get_center(self, obj):
        centroid = obj.center()
        if centroid:
            return {'type': 'Point', 'coordinates': [centroid.x, centroid.y]}
        return None

class LocationDetailsSerializer(serializers.ModelSerializer):
    sub_locations = LocationPropertiesSerializer(many=True, read_only=True)
    properties = serializers.SerializerMethodField()
    center = serializers.SerializerMethodField()
    class Meta:
        model=Location
        fields = ['id','name', 'location_type', 'geometry', 'average_price', 'center', 'properties', 'sub_locations']

    def get_properties(self, obj):
        # As propriedades já estão pré-carregadas com prefetch_related
        properties = obj.properties.all()
        return PropertySerializer(properties, many=True).data

    def get_center(self, obj):
        centroid = obj.center()
        if centroid:
            return {'type': 'Point', 'coordinates': [centroid.x, centroid.y]}
        return None

