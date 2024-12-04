#from django.db import models
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator


class Location(models.Model):
    LOCATION_TYPE=(
        ('N','Neighborhood'),
        ('CT','City'),
        ('S','State'),
        ('C','Country')
    )

    name=models.CharField(max_length=100)
    location_type=models.CharField(max_length=2, choices=LOCATION_TYPE, blank=False, null=False, default='N')
    geometry=models.MultiPolygonField(srid=4326, blank=True, null=True, geography=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_locations')

    objects=models.Manager()

    def __str__(self):
        return self.name

class Property(models.Model):
    class Meta:
        verbose_name_plural='Properties'

    PROPERTY_TYPE=(
        ('C','Casa'),
        ('A','Apartamento'),
        ('T','Terreno')
    )

    description=models.TextField()
    square_meters=models.FloatField(blank=False, null=False)
    bedrooms=models.IntegerField(blank=False, null=False, validators=[MinValueValidator(0)])
    bathrooms=models.IntegerField(blank=False, null=False, validators=[MinValueValidator(0)])
    price=models.FloatField(blank=False, null=False, validators=[MinValueValidator(0)])
    link=models.CharField(blank=False, null=False)
    listing_date=models.DateField(null=True)
    source=models.CharField(max_length=100, blank=False, null=False)
    property_type=models.CharField(max_length=1, choices=PROPERTY_TYPE, blank=False, null=False)
    location = models.ForeignKey(Location, related_name='properties',null=True, blank=True, on_delete= models.SET_NULL)
    coordinates = models.PointField(srid=4326, blank=False, null=True, geography=True)

    objects=models.Manager()

    def __str__(self):
        return self.link

class User(models.Model):
    name = models.CharField(blank=False, max_length=30)
    email = models.EmailField(blank=False, max_length=30)
    role=models.CharField(max_length=100, blank=False, null=False)

    objects=models.Manager()

    def __str__(self):
        return self.name