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
    list_display = ('id','name','location_type','geometry')
    list_display_links = ('id',)
    list_per_page = 20
    search_fields = ('id','name')

admin.site.register(Location, Locations)
