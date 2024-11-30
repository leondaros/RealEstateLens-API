from rest_framework import serializers
from real_estate_lens.models import User,Property,Location

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
        fields= ['name','location_type','geometry']

class LocationPropertiesSerializer(serializers.ModelSerializer):
    properties = PropertySerializer(many=True, read_only=True)
    class Meta:
        model=Location
        fields=['name','location_type','geometry','properties']