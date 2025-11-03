from rest_framework import viewsets, filters
from .models import Bike
from .serializers import BikeSerializer

class BikeViewSet(viewsets.ModelViewSet):
    queryset = Bike.objects.all().order_by('id')
    serializer_class = BikeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_serie', 'station__nombre', 'tipo', 'estado']
    ordering_fields = ['tipo', 'estado', 'fecha_registro']

    def get_queryset(self):
        """Permite filtrar por estación o tipo vía ?station_id=&tipo="""
        queryset = super().get_queryset()
        station_id = self.request.query_params.get('station_id')
        tipo = self.request.query_params.get('tipo')
        if station_id:
            queryset = queryset.filter(station_id=station_id)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset
