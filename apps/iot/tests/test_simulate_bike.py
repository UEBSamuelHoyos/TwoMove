import json
from unittest.mock import patch, MagicMock
from django.test import TestCase

from apps.iot.services.simulate_bike import (
    conectar_cliente,
    publicar_estado,
    simular_viaje,
    TOPIC,
    BIKE_ID,
    RUTA,
)


class TestSimulateBike(TestCase):
    """Pruebas unitarias para el simulador de bicicleta MQTT."""

    # ------------------------------------------------------------
    # 🔌 Test: conexión al broker MQTT
    # ------------------------------------------------------------
    @patch("apps.iot.services.simulate_bike.mqtt.Client")
    def test_conectar_cliente(self, mock_mqtt_client):
        """Debe crear un cliente y conectarse al broker correctamente."""
        mock_instance = MagicMock()
        mock_mqtt_client.return_value = mock_instance

        cliente = conectar_cliente()

        mock_instance.connect.assert_called_once_with("localhost", 1883, 60)
        self.assertEqual(cliente, mock_instance)

    # ------------------------------------------------------------
    # 📡 Test: publicación de estado
    # ------------------------------------------------------------
    @patch("apps.iot.services.simulate_bike.mqtt.Client")
    def test_publicar_estado(self, mock_mqtt_client):
        """Debe publicar un mensaje JSON con los campos correctos."""
        mock_client = MagicMock()
        lat, lon = 4.65, -74.24
        bateria = 98.5
        estado = "UNLOCKED"

        publicar_estado(mock_client, lat, lon, estado, bateria)

        # Debe haber llamado a publish con un JSON válido
        args, _ = mock_client.publish.call_args
        topic, payload = args
        self.assertEqual(topic, TOPIC)

        data = json.loads(payload)
        self.assertEqual(data["bikeId"], BIKE_ID)
        self.assertEqual(data["latitude"], lat)
        self.assertEqual(data["longitude"], lon)
        self.assertEqual(data["battery"], bateria)
        self.assertEqual(data["lockStatus"], estado)
        self.assertIn("timestamp", data)

    # ------------------------------------------------------------
    # 🚲 Test: simulación completa del viaje
    # ------------------------------------------------------------
    @patch("apps.iot.services.simulate_bike.random.uniform", return_value=1.0)
    @patch("apps.iot.services.simulate_bike.time.sleep", return_value=None)
    @patch("apps.iot.services.simulate_bike.mqtt.Client")
    def test_simular_viaje_completo(self, mock_mqtt_client, mock_sleep, mock_rand):
        """Debe simular un viaje completo publicando múltiples mensajes MQTT."""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client

        simular_viaje()

        # Total de mensajes:
        #   1 LOCKED inicial + 1 UNLOCKED + len(RUTA) puntos + 1 LOCKED final
        expected_msgs = 2 + len(RUTA) + 1
        self.assertEqual(mock_client.publish.call_count, expected_msgs)

        # Se espera que se haya conectado una vez
        mock_client.connect.assert_called_once_with("localhost", 1883, 60)

        # Se espera que haya dormido varias veces
        self.assertTrue(mock_sleep.call_count >= 3)

        # Último mensaje debe tener lockStatus = LOCKED
        last_call = mock_client.publish.call_args_list[-1]
        payload = json.loads(last_call[0][1])
        self.assertEqual(payload["lockStatus"], "LOCKED")
