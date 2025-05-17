from django.contrib import admin
from real_estate_lens.models import User,Property,Location, FavoriteLocation

class FavoriteLocationInline(admin.TabularInline):
    model = FavoriteLocation
    extra = 0                  # nenhum form extra vazio
    readonly_fields = ('favorited_at',)  # timestamps não editáveis
    autocomplete_fields = ('location',)  # se usar search/autocomplete no admin
    verbose_name = "Favorito"
    verbose_name_plural = "Favoritos"

class Users(admin.ModelAdmin):
    list_display = ('id','name','email','role')
    list_display_links = ('id','name')
    list_per_page = 20
    search_fields = ('name','email')
    inlines = [FavoriteLocationInline]

admin.site.register(User,Users)

class Properties(admin.ModelAdmin):
    list_display = (
        'id',
        'square_meters',
        'bedrooms',
        'bathrooms',
        'price',
        'link',
        'listing_date',
        'source',
        'property_type'
    )
    list_display_links = ('id','property_type')
    list_per_page = 20
    search_fields = ('bedrooms','bathrooms','square_meters','price')

admin.site.register(Property,Properties)


class Locations(admin.ModelAdmin):
    list_display = ('id','name','location_type')
    list_display_links = ('id',)
    list_per_page = 20
    search_fields = ('id','name')
    inlines = [FavoriteLocationInline]

admin.site.register(Location, Locations)

class FavoriteLocations(admin.ModelAdmin):
    list_display = ('user', 'location', 'favorited_at')
    list_filter = ('favorited_at', 'location')
    search_fields = ('user__name', 'location__name')
    autocomplete_fields = ('user', 'location')

admin.site.register(FavoriteLocation, FavoriteLocations)