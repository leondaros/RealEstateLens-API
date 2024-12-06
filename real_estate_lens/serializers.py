from rest_framework import serializers
from real_estate_lens.models import User,Property,Location
from django.db.models import Avg
import locale

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields= '__all__'

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model=Property
        fields= ['description', 'square_meters', 'bedrooms', 'bathrooms',
                 'price', 'link', 'listing_date', 'source', 'property_type',
                 'location', 'coordinates']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Location
        fields= ['name','location_type','geometry','average_price']

class LocationPropertiesSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()
    class Meta:
        model=Location
        fields=['name','location_type','geometry','average_price','properties']

    def get_properties(self, obj):
        # As propriedades já estão pré-carregadas com prefetch_related
        properties = obj.properties.all()
        return PropertySerializer(properties, many=True).data

class LocationDetailsSerializer(serializers.ModelSerializer):
    sub_locations = LocationPropertiesSerializer(many=True, read_only=True)
    properties = serializers.SerializerMethodField()
    class Meta:
        model=Location
        fields = ['name', 'location_type', 'geometry', 'average_price', 'properties', 'sub_locations']

    def get_properties(self, obj):
        # As propriedades já estão pré-carregadas com prefetch_related
        properties = obj.properties.all()
        return PropertySerializer(properties, many=True).data

