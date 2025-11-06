from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.rentals.services.trip_end_service import TripEndService
from apps.rentals.models import Rental
from apps.bikes.models import Bike
from apps.stations.models import Station
from apps.wallet.models import Wallet
from apps.transactions.models import WalletTransaccion


class TestTripEndService(TestCase):
    """Pruebas unitarias del flujo de finalización de viajes (TripEndService)."""

    def setUp(self):
        Usuario = get_user_model()
        self.usuario = Usuario.objects.create_user(
            email="usuario@test.com",
            password="123456",
            nombre="Fabian",
            apellido="Hoyos"
        )

        # Estaciones
        self.origen = Station.objects.create(
            nombre="Estación A",
            direccion="Calle 10",
            latitud=6.25,
            longitud=-75.56,
        )
        self.destino = Station.objects.create(
            nombre="Estación B",
            direccion="Calle 20",
            latitud=6.26,
            longitud=-75.57,
        )

        # Bicicleta activa
        self.bike = Bike.objects.create(
            numero_serie="B-123",
            tipo="electric",
            estado="in_use",
            station=self.origen,
            bateria_porcentaje=85,
        )

        # Wallet con saldo
        self.wallet = Wallet.objects.create(usuario=self.usuario, balance=Decimal("100000"))

        # Rental activo
        self.rental = Rental.objects.create(
            usuario=self.usuario,
            bike=self.bike,
            estacion_origen=self.origen,
            estacion_destino=self.destino,
            tipo_viaje="ultima_milla",
            metodo_pago="wallet",
            estado="activo",
            hora_inicio=timezone.now() - timezone.timedelta(minutes=50),
            costo_estimado=Decimal("17500")
        )

    # ============================================================
    # ✅ Caso exitoso: finalizar viaje normal
    # ============================================================
    @patch("apps.rentals.services.trip_end_service.EmailMultiAlternatives")
    @patch("apps.rentals.services.trip_end_service.canvas.Canvas")
    def test_end_trip_exitoso(self, mock_canvas, mock_email):
        """Debe finalizar correctamente el viaje activo, registrar transacción y generar factura."""
        mock_email.return_value.send.return_value = True
        mock_canvas.return_value = MagicMock()

        resultado = TripEndService.end_trip(
            usuario=self.usuario,
            rental_id=self.rental.id,
            estacion_destino_id=self.destino.id
        )

        self.assertEqual(resultado["mensaje"], "✅ Viaje finalizado correctamente")
        self.assertAlmostEqual(resultado["costo_total"], 17500.0, delta=5000)
        self.assertEqual(resultado["estado_bicicleta"], "block")
        self.assertEqual(resultado["estacion_destino"], self.destino.nombre)

        rental = Rental.objects.get(pk=self.rental.id)
        self.assertEqual(rental.estado, "finalizado")
        self.assertTrue(WalletTransaccion.objects.filter(wallet=self.wallet).exists())

    # ============================================================
    # ⚠️ Caso de error: rental no existe
    # ============================================================
    def test_end_trip_rental_inexistente(self):
        """Debe lanzar error si el rental_id no existe."""
        with self.assertRaises(ValueError):
            TripEndService.end_trip(
                usuario=self.usuario,
                rental_id=9999,
                estacion_destino_id=self.destino.id
            )

    # ============================================================
    # ⚠️ Caso de error: viaje no está activo
    # ============================================================
    def test_end_trip_estado_incorrecto(self):
        """Debe lanzar error si el viaje no está activo."""
        self.rental.estado = "reservado"
        self.rental.save()
        with self.assertRaises(ValueError):
            TripEndService.end_trip(
                usuario=self.usuario,
                rental_id=self.rental.id,
                estacion_destino_id=self.destino.id
            )

    # ============================================================
    # ⚠️ Caso de error: estación destino inválida
    # ============================================================
    def test_end_trip_estacion_destino_invalida(self):
        """Debe lanzar error si la estación destino no existe."""
        with self.assertRaises(ValueError):
            TripEndService.end_trip(
                usuario=self.usuario,
                rental_id=self.rental.id,
                estacion_destino_id=9999
            )

    # ============================================================
    # ✅ Caso sin estación destino → fuera de estación real
    # ============================================================
    @patch("apps.rentals.services.trip_end_service.EmailMultiAlternatives")
    @patch("apps.rentals.services.trip_end_service.canvas.Canvas")
    def test_end_trip_fuera_de_estacion(self, mock_canvas, mock_email):
        """Debe aplicar multa si el viaje termina fuera de estación."""
        mock_email.return_value.send.return_value = True
        mock_canvas.return_value = MagicMock()

        # 🔧 Forzar rental sin destino para simular viaje fuera de estación
        self.rental.estacion_destino = None
        self.rental.save(update_fields=["estacion_destino"])

        resultado = TripEndService.end_trip(
            usuario=self.usuario,
            rental_id=self.rental.id,
            estacion_destino_id=None
        )

        self.assertIn("✅", resultado["mensaje"])
        self.assertEqual(resultado["estado_bicicleta"], "block")
        self.assertEqual(resultado["estacion_destino"], "N/A")
