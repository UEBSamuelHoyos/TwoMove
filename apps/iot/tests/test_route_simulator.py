from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from apps.iot.services.route_simulator import simulate_bike_route, get_route_points
from apps.stations.models import Station
from apps.bikes.models import Bike
from apps.rentals.models import Rental


class TestSimulateBikeRoute(TestCase):
    """Pruebas para el simulador de rutas IoT y la función get_route_points."""

    def setUp(self):
        User = get_user_model()
        self.usuario = User.objects.create(
            email="testuser@example.com",
            password="123456"
        )

        # Crear estaciones
        self.start = Station.objects.create(
            nombre="Origen",
            direccion="Calle 1",
            latitud=6.25184,
            longitud=-75.56359,
        )
        self.end = Station.objects.create(
            nombre="Destino",
            direccion="Calle 2",
            latitud=6.26000,
            longitud=-75.57000,
        )

        # Crear bicicleta
        self.bike = Bike.objects.create(
            numero_serie="E-001",
            tipo="electric",
            estado="available",
            station=self.start,
            bateria_porcentaje=95,
        )

        # Crear alquiler con usuario obligatorio
        self.rental = Rental.objects.create(
            usuario=self.usuario,
            bike=self.bike,
            estacion_origen=self.start,
            estacion_destino=self.end,
            estado="iniciado",
        )

    # =========================================================
    # 🗺️ Prueba de rutas OSRM
    # =========================================================
    @patch("apps.iot.services.route_simulator.requests.get")
    def test_get_route_points_valido(self, mock_get):
        """Debe devolver coordenadas válidas convertidas de OSRM."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "routes": [
                {
                    "geometry": {
                        "coordinates": [
                            [-75.56359, 6.25184],
                            [-75.56400, 6.25200],
                            [-75.57000, 6.26000],
                        ]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        coords = get_route_points(6.25184, -75.56359, 6.26000, -75.57000)
        self.assertEqual(len(coords), 3)
        self.assertEqual(coords[0], (6.25184, -75.56359))
        self.assertEqual(coords[-1], (6.26000, -75.57000))

    @patch("apps.iot.services.route_simulator.requests.get", side_effect=Exception("Error de red"))
    def test_get_route_points_falla_y_devuelve_linea_recta(self, _):
        """Si OSRM falla, debe retornar una línea recta simple."""
        coords = get_route_points(1.0, 2.0, 3.0, 4.0)
        self.assertEqual(coords, [(1.0, 2.0), (3.0, 4.0)])

    # =========================================================
    # 🚲 Prueba de simulación de ruta
    # =========================================================
    @patch("apps.iot.services.route_simulator.mqtt.Client")
    @patch("apps.iot.services.route_simulator.get_route_points")
    @patch("apps.iot.services.route_simulator.time.sleep", return_value=None)
    def test_simulate_bike_route_envia_mensajes(self, mock_sleep, mock_get_route, mock_mqtt_client):
        """Debe publicar múltiples mensajes MQTT simulando la ruta."""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client
        mock_get_route.return_value = [
            (6.25184, -75.56359),
            (6.25200, -75.56400),
            (6.26000, -75.57000),
        ]

        simulate_bike_route(self.rental.id)

        # Conexión
        mock_client.connect.assert_called_once_with("localhost", 1883, 60)
        # Publicaciones
        self.assertEqual(mock_client.publish.call_count, 3)
        # Desconexión
        mock_client.disconnect.assert_called_once()

    @patch("apps.iot.services.route_simulator.mqtt.Client")
    def test_simulate_bike_route_rental_inexistente(self, mock_mqtt_client):
        """Si el rental no existe, no debe conectarse al broker."""
        simulate_bike_route(9999)
        mock_mqtt_client.assert_not_called()
