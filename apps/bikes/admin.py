from django.contrib import admin
from .models import Bike

@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    list_display = ('numero_serie', 'tipo', 'estado', 'fecha_registro')
    list_filter = ('tipo', 'estado')
    search_fields = ('numero_serie',)
    ordering = ('-fecha_registro',)
