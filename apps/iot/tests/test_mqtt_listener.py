from django.test import TestCase
from unittest.mock import MagicMock
from datetime import datetime
from apps.iot.models import BikeTelemetry
from apps.iot.services import mqtt_listener


class TestMQTTListener(TestCase):
    """
    Pruebas unitarias del servicio de escucha MQTT (apps/iot/services/mqtt_listener.py).
    Se valida que el callback on_message procese correctamente la telemetría recibida.
    """

    def setUp(self):
        BikeTelemetry.objects.all().delete()

    def test_mensaje_valido_crea_registro(self):
        """Debe crear un registro válido de telemetría al recibir un mensaje completo."""
        payload = {
            "bike_id": 1,
            "lat": 6.25184,
            "lon": -75.56359,
            "bateria": 85.5,
            "velocidad": 12.3,
            "timestamp": str(datetime.now()),
        }
        msg = MagicMock()
        msg.payload = str(payload).replace("'", '"').encode()  # JSON simulado

        mqtt_listener.on_message(None, None, msg)

        telemetrias = BikeTelemetry.objects.all()
        self.assertEqual(telemetrias.count(), 1)

        t = telemetrias.first()
        self.assertEqual(t.bike_id, 1)
        self.assertAlmostEqual(float(t.latitude), 6.25184, places=5)
        self.assertEqual(t.lock_status, "UNLOCKED")
        self.assertTrue(60 <= t.battery <= 100)

    def test_mensaje_sin_coordenadas_no_crea_registro(self):
        """Debe ignorar mensajes sin lat/lon válidas."""
        payload = {"bike_id": 2, "lat": None, "lon": None}
        msg = MagicMock()
        msg.payload = str(payload).replace("'", '"').encode()

        mqtt_listener.on_message(None, None, msg)

        self.assertEqual(BikeTelemetry.objects.count(), 0)

    def test_mensaje_sin_bike_id_no_crea_registro(self):
        """Debe ignorar mensajes sin identificador de bicicleta."""
        payload = {"lat": 10.0, "lon": 20.0}
        msg = MagicMock()
        msg.payload = str(payload).replace("'", '"').encode()

        mqtt_listener.on_message(None, None, msg)

        self.assertEqual(BikeTelemetry.objects.count(), 0)

    def test_mensaje_malformado_no_rompe(self):
        """Debe manejar errores de parsing sin lanzar excepción."""
        msg = MagicMock()
        msg.payload = b"{malformed_json}"

        try:
            mqtt_listener.on_message(None, None, msg)
        except Exception as e:
            self.fail(f"No debería lanzar excepción, pero lanzó: {e}")

        self.assertEqual(BikeTelemetry.objects.count(), 0)
