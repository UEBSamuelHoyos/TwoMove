import json
import threading
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.iot.services.start_simulation_service import (
    get_route_points,
    simulate_bike_route,
    simulate_route_async,
)
from apps.stations.models import Station
from apps.bikes.models import Bike
from apps.rentals.models import Rental


class TestStartSimulationService(TestCase):
    """Pruebas para el servicio de simulación IoT con hilos."""

    def setUp(self):
        User = get_user_model()
        self.usuario = User.objects.create(
            email="testuser@example.com",
            password="123456"
        )

        self.origen = Station.objects.create(
            nombre="Estación A",
            direccion="Calle 10",
            latitud=6.25184,
            longitud=-75.56359,
        )
        self.destino = Station.objects.create(
            nombre="Estación B",
            direccion="Calle 20",
            latitud=6.26000,
            longitud=-75.57000,
        )

        self.bike = Bike.objects.create(
            numero_serie="E-123",
            tipo="electric",
            estado="available",
            station=self.origen,
            bateria_porcentaje=90,
        )

        self.rental = Rental.objects.create(
            usuario=self.usuario,
            bike=self.bike,
            estacion_origen=self.origen,
            estacion_destino=self.destino,
            estado="iniciado",
        )

    # ============================================================
    # 🗺️ Pruebas para get_route_points
    # ============================================================
    @patch("apps.iot.services.start_simulation_service.requests.get")
    def test_get_route_points_valido(self, mock_get):
        """Debe devolver coordenadas válidas desde OSRM."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "routes": [
                {
                    "geometry": {
                        "coordinates": [
                            [-75.56359, 6.25184],
                            [-75.57000, 6.26000],
                        ]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        coords = get_route_points(6.25184, -75.56359, 6.26000, -75.57000)
        self.assertEqual(coords, [(6.25184, -75.56359), (6.26000, -75.57000)])

    @patch("apps.iot.services.start_simulation_service.requests.get", side_effect=Exception("error"))
    def test_get_route_points_fallback(self, _):
        """Si OSRM falla, debe devolver línea recta."""
        coords = get_route_points(1.0, 2.0, 3.0, 4.0)
        self.assertEqual(coords, [(1.0, 2.0), (3.0, 4.0)])

    # ============================================================
    # 🚴 Pruebas para simulate_bike_route
    # ============================================================
    @patch("apps.iot.services.start_simulation_service.get_route_points")
    @patch("apps.iot.services.start_simulation_service.mqtt.Client")
    @patch("apps.iot.services.start_simulation_service.time.sleep", return_value=None)
    def test_simulate_bike_route_envia_mensajes(self, mock_sleep, mock_mqtt_client, mock_route):
        """Debe publicar mensajes MQTT según la ruta generada."""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client
        mock_route.return_value = [
            (6.25, -75.56),
            (6.26, -75.57),
        ]

        simulate_bike_route(self.rental.id)

        # Conexión al broker
        mock_client.connect.assert_called_once_with("localhost", 1883, 60)
        # Publicación de mensajes
        self.assertEqual(mock_client.publish.call_count, len(mock_route.return_value))
        # Desconexión
        mock_client.disconnect.assert_called_once()

    @patch("apps.iot.services.start_simulation_service.mqtt.Client")
    def test_simulate_bike_route_rental_inexistente(self, mock_mqtt_client):
        """Si el rental no existe, no debe conectarse ni publicar."""
        simulate_bike_route(999)
        mock_mqtt_client.assert_not_called()

    # ============================================================
    # 🧵 Prueba para simulate_route_async
    # ============================================================
    @patch("apps.iot.services.start_simulation_service.threading.Thread")
    def test_simulate_route_async_crea_hilo(self, mock_thread):
        """Debe crear y lanzar un hilo en background."""
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        simulate_route_async(123)

        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        self.assertTrue(mock_thread_instance.daemon)
