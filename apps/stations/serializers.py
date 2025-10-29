from rest_framework import serializers
from .models import Station

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = [
            'id',
            'nombre',
            'direccion',
            'latitud',
            'longitud',
            'capacidad_electricas',
            'capacidad_mecanicas',
            'disponibles_electricas',
            'disponibles_mecanicas',
            'total_disponibles',
        ]
