from rest_framework import serializers
from .models import Bike

class BikeSerializer(serializers.ModelSerializer):
    station_nombre = serializers.CharField(source='station.nombre', read_only=True)

    class Meta:
        model = Bike
        fields = [
            'id', 'numero_serie', 'tipo', 'estado', 
            'station', 'station_nombre', 
            'fecha_registro', 'fecha_actualizacion'
        ]
