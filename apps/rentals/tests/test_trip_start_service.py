from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.rentals.services.trip_start_service import TripStartService
from apps.rentals.models import Rental
from apps.bikes.models import Bike
from apps.stations.models import Station


class TestTripStartService(TestCase):
    """Pruebas unitarias para TripStartService (inicio de viaje)."""

    def setUp(self):
        Usuario = get_user_model()
        self.usuario = Usuario.objects.create_user(
            email="usuario@test.com",
            password="123456",
            nombre="Fabian",
            apellido="Hoyos"
        )

        self.estacion_origen = Station.objects.create(
            nombre="Estación A",
            direccion="Calle 10",
            latitud=6.25,
            longitud=-75.56,
        )
        self.estacion_destino = Station.objects.create(
            nombre="Estación B",
            direccion="Calle 20",
            latitud=6.26,
            longitud=-75.57,
        )

        self.bike = Bike.objects.create(
            numero_serie="B-123",
            tipo="electric",
            estado="disponible",
            station=self.estacion_origen,
            bateria_porcentaje=90,
        )

        self.rental = Rental.objects.create(
            usuario=self.usuario,
            bike=self.bike,
            estacion_origen=self.estacion_origen,
            estacion_destino=self.estacion_destino,
            tipo_viaje="ultima_milla",
            metodo_pago="wallet",
            estado="reservado",
            bike_serial_reservada="B-123",
            codigo_desbloqueo="ABCD12",
            costo_estimado=Decimal("17500"),
        )

    # ============================================================
    # ✅ Caso exitoso (start_trip_by_user)
    # ============================================================
    @patch("apps.rentals.services.trip_start_service.EmailMultiAlternatives")
    @patch("apps.rentals.services.trip_start_service.simulate_route_async")
    def test_start_trip_by_user_exitoso(self, mock_sim, mock_email):
        """Debe iniciar el viaje correctamente desde start_trip_by_user."""
        mock_sim.return_value = True
        mock_email.return_value.send.return_value = True

        resultado = TripStartService.start_trip_by_user(
            user_pk=self.usuario.pk,
            codigo="ABCD12"
        )

        self.assertEqual(resultado["estado"], "activo")
        self.assertIn("Viaje iniciado", resultado["mensaje"])

        rental = Rental.objects.get(pk=self.rental.id)
        self.assertEqual(rental.estado, "activo")
        self.assertIsNotNone(rental.hora_inicio)
        self.assertEqual(rental.bike.estado, "en_uso")

    # ============================================================
    # ✅ Caso exitoso (start_trip clásico)
    # ============================================================
    @patch("apps.rentals.services.trip_start_service.EmailMultiAlternatives")
    @patch("apps.rentals.services.trip_start_service.simulate_route_async")
    def test_start_trip_clasico_exitoso(self, mock_sim, mock_email):
        """Debe iniciar el viaje correctamente usando start_trip clásico."""
        mock_sim.return_value = True
        mock_email.return_value.send.return_value = True

        resultado = TripStartService.start_trip(
            user=self.usuario,
            rental_id=self.rental.id,
            codigo="ABCD12"
        )

        self.assertEqual(resultado["estado"], "activo")
        self.assertIn("Bicicleta desbloqueada", resultado["mensaje"])

    # ============================================================
    # ⚠️ Error: Falta PK o código
    # ============================================================
    def test_start_trip_by_user_falta_datos(self):
        """Debe lanzar error si falta user_pk o código."""
        with self.assertRaises(ValueError):
            TripStartService.start_trip_by_user(user_pk=None, codigo="1234")

        with self.assertRaises(ValueError):
            TripStartService.start_trip_by_user(user_pk=self.usuario.pk, codigo="")

    # ============================================================
    # ⚠️ Error: sin reservas activas
    # ============================================================
    def test_start_trip_by_user_sin_reserva(self):
        """Debe lanzar error si no hay reservas activas."""
        Rental.objects.all().delete()
        with self.assertRaises(ValueError):
            TripStartService.start_trip_by_user(user_pk=self.usuario.pk, codigo="1234")

    # ============================================================
    # ⚠️ Error: múltiples reservas
    # ============================================================
    def test_start_trip_by_user_multiples_reservas(self):
        """Debe lanzar error si el usuario tiene varias reservas en estado reservado."""
        Rental.objects.create(
            usuario=self.usuario,
            bike=self.bike,
            estacion_origen=self.estacion_origen,
            tipo_viaje="ultima_milla",
            metodo_pago="wallet",
            estado="reservado",
            codigo_desbloqueo="XYZ999",
        )
        with self.assertRaises(ValueError):
            TripStartService.start_trip_by_user(user_pk=self.usuario.pk, codigo="ABCD12")

    # ============================================================
    # ⚠️ Error: código incorrecto
    # ============================================================
    def test_start_trip_codigo_incorrecto(self):
        """Debe lanzar error si el código no coincide con los válidos."""
        with self.assertRaises(ValueError):
            TripStartService._activate_rental(self.rental, codigo="ZZZZ99")

    # ============================================================
    # ⚠️ Error: reserva en estado inválido
    # ============================================================
    def test_start_trip_estado_invalido(self):
        """Debe lanzar error si la reserva no está en estado 'reservado'."""
        self.rental.estado = "activo"
        self.rental.save()
        with self.assertRaises(ValueError):
            TripStartService._activate_rental(self.rental, codigo="ABCD12")

    # ============================================================
    # ⚙️ Caso sin estaciones (no lanza simulación)
    # ============================================================
    @patch("apps.rentals.services.trip_start_service.EmailMultiAlternatives")
    @patch("apps.rentals.services.trip_start_service.simulate_route_async")
    def test_start_trip_sin_estaciones(self, mock_sim, mock_email):
        """Debe iniciar el viaje pero no lanzar simulación IoT si faltan estaciones."""
        self.rental.estacion_destino = None
        self.rental.save(update_fields=["estacion_destino"])
        mock_sim.return_value = True
        mock_email.return_value.send.return_value = True

        resultado = TripStartService._activate_rental(self.rental, codigo="ABCD12")
        self.assertEqual(resultado["estado"], "activo")
        mock_sim.assert_not_called()
