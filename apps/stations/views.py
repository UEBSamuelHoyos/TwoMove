from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from .models import Station
from .serializers import StationSerializer  # ← importante

class StationViewSet(viewsets.ModelViewSet):
    """
    API para gestionar estaciones del sistema.
    Permite listar, crear, editar y eliminar estaciones.
    Incluye filtros por nombre y ordenamiento por campos.
    """
    queryset = Station.objects.all().order_by('nombre')
    serializer_class = StationSerializer  # ← esta línea arregla el error
    permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'direccion']
    ordering_fields = [
        'nombre', 
        'capacidad_electricas', 
        'capacidad_mecanicas', 
        'total_disponibles'
    ]

    def get_queryset(self):
        """
        Permite filtrar por nombre de estación o por disponibilidad mínima.
        Ejemplo:
          /api/stations/?min_disponibles=5
        """
        queryset = super().get_queryset()
        nombre = self.request.query_params.get('nombre')
        min_disp = self.request.query_params.get('min_disponibles')

        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        if min_disp:
            try:
                min_disp = int(min_disp)
                queryset = [
                    s for s in queryset 
                    if s.total_disponibles >= min_disp
                ]
            except ValueError:
                pass

        return queryset
