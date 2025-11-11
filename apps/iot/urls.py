from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BikeTelemetryViewSet
from apps.iot.services.view_dashboard import iot_dashboard

router = DefaultRouter()
router.register(r"telemetry", BikeTelemetryViewSet, basename="telemetry")

urlpatterns = [
    path("api/", include(router.urls)),
    path("monitor/", iot_dashboard, name="iot_dashboard"),
]
