from django.shortcuts import render
from apps.iot.models import BikeTelemetry

def iot_dashboard(request):
    """
    Muestra el mapa con la posición actual de todas las bicicletas simuladas.
    """
    # Obtenemos la última telemetría por bicicleta (agrupada)
    ultimos_registros = (
        BikeTelemetry.objects.order_by("bike_id", "-timestamp")
        .distinct("bike_id")
    )

    context = {
        "telemetria": ultimos_registros,
    }
    return render(request, "iot/dashboard.html", context)
