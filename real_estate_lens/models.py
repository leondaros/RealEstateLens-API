from django.db import models
from django.core.validators import MinValueValidator


class Location(models.Model):
    district=models.CharField()
    city=models.CharField()
    latitude = models.FloatField(blank=False, null=False)
    longitude = models.FloatField(blank=False, null=False)

    objects=models.Manager()

    def __str__(self):
        return self.district

class Property(models.Model):
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
    listing_date=models.DateField()
    source=models.CharField(blank=False, null=False)
    property_type=models.CharField(choices=PROPERTY_TYPE, blank=False, null=False)
    location = models.ForeignKey(Location, null=True, on_delete= models.CASCADE)

    objects=models.Manager()

    def __str__(self):
        return self.link

class User(models.Model):
    name = models.CharField(blank=False, max_length=30)
    email = models.EmailField(blank=False, max_length=30)
    role=models.CharField(blank=False, null=False)

    objects=models.Manager()

    def __str__(self):
        return self.name