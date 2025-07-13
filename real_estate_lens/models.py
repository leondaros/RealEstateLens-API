#from django.db import models
from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator
from django.db.models import Avg
from django.db.models import UniqueConstraint
from django.contrib.auth.models import AbstractUser, UserManager

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

    def average_price(self):
        # Calcula a média dos preços dos imóveis relacionados
        avg_price = self.properties.aggregate(Avg('price'))['price__avg']
        return round(avg_price,2) if avg_price is not None else 0.00

    def center(self):
        if not self.geometry:
            return None

        # geometry.centroid is already a Point
        center_point = self.geometry.point_on_surface

        # ensure it has the correct SRID
        if center_point.srid != self.geometry.srid:
            center_point.srid = self.geometry.srid

        return center_point

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

    def update_location(self, location_id):

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            raise ValueError("Location com o ID fornecido não existe.")

        # Verifica se ambos os campos geométricos existem
        if not self.coordinates or not location.geometry:
            raise ValueError("Os dados geométricos da Propriedade ou Localização estão ausentes.")

        if self.coordinates.within(location.geometry):
            self.location=location
            self.save()
            return True
        return False

    def __str__(self):
        return self.link

class FavoriteLocation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_locations_links'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        related_name='favorited_by_links'
    )
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Nome explícito da tabela, em snake_case
        db_table = 'user_favorite_locations'
        # Constraint moderna e nomeada
        constraints = [
            UniqueConstraint(
                fields=['user', 'location'],
                name='uniq_user_favorite_location'
            )
        ]
        # Ordenação padrão (por data decrescente)
        ordering = ['-favorited_at']

    def __str__(self):
        return f'{self.user} ❤️ {self.location}'

class User(AbstractUser):
    # Campos extras
    role=models.CharField(max_length=100, blank=False, null=False)

    favorite_locations = models.ManyToManyField(
        'Location',
        through='FavoriteLocation',
        related_name='favorited_by',
        blank=True
    )

    objects=UserManager()

    def __str__(self):
        return self.username