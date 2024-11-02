from django.contrib import admin
from real_estate_lens.models import User,Property,Location

class Users(admin.ModelAdmin):
    list_display = ('id','name','email','role')
    list_display_links = ('id','name')
    list_per_page = 20
    search_fields = ('name','email')

admin.site.register(User,Users)

class Properties(admin.ModelAdmin):
    list_display = (
        'id',
        'description',
        'square_meters',
        'bedrooms',
        'bathrooms',
        'price',
        'link',
        'listing_date',
        'source',
        'property_type',
        'location'
    )
    list_display_links = ('id','property_type')
    list_per_page = 20
    search_fields = ('bedrooms','bathrooms','square_meters','price')

admin.site.register(Property,Properties)


class Locations(admin.ModelAdmin):
    list_display = ('id','district','city','latitude','longitude')
    list_display_links = ('id','district','city')
    list_per_page = 20
    search_fields = ('district','city')

admin.site.register(Location, Locations)
