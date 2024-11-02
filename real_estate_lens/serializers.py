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