import pytest
from django.test import RequestFactory
from django.utils import timezone

from apps.iot.services.view_dashboard import iot_dashboard
from apps.iot.models import BikeTelemetry
from apps.bikes.models import Bike


@pytest.mark.django_db
class TestIotDashboardService:
    """Pruebas unitarias para la vista iot_dashboard (en services)."""

    def setup_method(self):
        self.factory = RequestFactory()

        # Crear bicicletas de prueba
        self.bike1 = Bike.objects.create(
            numero_serie="E-001",
            tipo="electric",
            estado="available",
            bateria_porcentaje=90,
        )
        self.bike2 = Bike.objects.create(
            numero_serie="M-002",
            tipo="manual",
            estado="available",
            bateria_porcentaje=100,
        )

        # Crear telemetrías de prueba
        BikeTelemetry.objects.create(
            bike_id=self.bike1.id,
            latitude=6.25184,
            longitude=-75.56359,
            battery=85.0,
            lock_status="UNLOCKED",
            timestamp=timezone.now(),
        )
        BikeTelemetry.objects.create(
            bike_id=self.bike1.id,
            latitude=6.25200,
            longitude=-75.56400,
            battery=83.0,
            lock_status="LOCKED",
            timestamp=timezone.now() + timezone.timedelta(seconds=10),
        )
        BikeTelemetry.objects.create(
            bike_id=self.bike2.id,
            latitude=6.30000,
            longitude=-75.60000,
            battery=90.0,
            lock_status="UNLOCKED",
            timestamp=timezone.now(),
        )

    # ------------------------------------------------------------------
    def test_iot_dashboard_renderiza_correctamente(self):
        """Debe renderizar el template correcto y responder 200."""
        request = self.factory.get("/iot/dashboard/")
        response = iot_dashboard(request)

        assert response.status_code == 200
        assert "iot/dashboard.html" in [t.name for t in response.templates]

    # ------------------------------------------------------------------
    def test_iot_dashboard_contexto_con_telemetria(self):
        """Debe incluir la última telemetría de cada bicicleta."""
        request = self.factory.get("/iot/dashboard/")
        response = iot_dashboard(request)
        context = getattr(response, "context_data", response.context)

        assert "telemetria" in context
        telemetria = list(context["telemetria"])
        assert len(telemetria) == 2  # una por cada bike_id

        # Verifica que cada bike_id tenga su registro más reciente
        latest_bike1 = BikeTelemetry.objects.filter(bike_id=self.bike1.id).latest("timestamp")
        latest_bike2 = BikeTelemetry.objects.filter(bike_id=self.bike2.id).latest("timestamp")

        timestamps = [t.timestamp for t in telemetria]
        assert latest_bike1.timestamp in timestamps
        assert latest_bike2.timestamp in timestamps

    # ------------------------------------------------------------------
    def test_iot_dashboard_sin_registros(self):
        """Debe manejar correctamente el caso sin telemetría."""
        BikeTelemetry.objects.all().delete()

        request = self.factory.get("/iot/dashboard/")
        response = iot_dashboard(request)
        context = getattr(response, "context_data", response.context)

        assert "telemetria" in context
        assert list(context["telemetria"]) == []
