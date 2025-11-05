from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.db.models import Max

from .models import BikeTelemetry
from .serializers import BikeTelemetrySerializer


class BikeTelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API pública para consultar la telemetría más reciente de cada bicicleta.
    """
    serializer_class = BikeTelemetrySerializer
    permission_classes = [AllowAny]  # puedes cambiar a IsAuthenticated si lo prefieres

    def get_queryset(self):
        """
        Devuelve la última telemetría registrada por cada bicicleta.
        """
        # Subconsulta para obtener el último registro por bike_id
        subquery = (
            BikeTelemetry.objects.values("bike_id")
            .annotate(last_id=Max("id"))
            .values_list("last_id", flat=True)
        )
        return BikeTelemetry.objects.filter(id__in=subquery).order_by("bike_id")

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Alias directo para obtener los últimos registros (igual a list)."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
