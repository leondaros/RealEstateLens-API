from rest_framework import serializers
from real_estate_lens.models import User,Property,Location

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields= '__all__'

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model=Property
        fields= '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Location
        fields= '__all__'

class ListPropertiesLocationSerializer(serializers.ModelSerializer):
    location_district=serializers.ReadOnlyField(source='location.district')
    class Meta:
        model=Property
        fields=['location_district','price']