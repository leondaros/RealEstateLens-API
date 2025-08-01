from rest_framework import serializers
from django.contrib.auth import get_user_model
from real_estate_lens.models import Property,Location
from django.db.models import Avg
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    favorite_locations = serializers.SerializerMethodField()
    class Meta:
        model=User
        fields= ['id', 'username', 'email', 'role', 'favorite_locations']

    def get_favorite_locations(self, obj):
        return LocationSummarySerializer(obj.favorite_locations.all(), many=True).data
    
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', '')
        )
        return user

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
        fields= ['id','name','location_type','geometry','average_price_per_m2','center']

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
        fields=['id','name','location_type','geometry','average_price_per_m2','center','properties']

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
        fields = ['id','name', 'location_type', 'geometry', 'average_price_per_m2', 'center', 'properties', 'sub_locations']

    def get_properties(self, obj):
        # As propriedades já estão pré-carregadas com prefetch_related
        properties = obj.properties.all()
        return PropertySerializer(properties, many=True).data

    def get_center(self, obj):
        centroid = obj.center()
        if centroid:
            return {'type': 'Point', 'coordinates': [centroid.x, centroid.y]}
        return None

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role
        }
        return data
