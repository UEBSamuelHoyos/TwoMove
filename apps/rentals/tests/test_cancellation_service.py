from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.rentals.models import Rental
from apps.rentals.services.cancellation_service import CancellationService
from apps.wallet.models import Wallet


class TestCancellationService(TestCase):
    """Pruebas unitarias para el servicio CancellationService."""

    def setUp(self):
        """Crea usuario, estaciones, bicicleta y reserva base."""
        User = get_user_model()
        self.usuario = User.objects.create(
            email="usuario@test.com",
            password="123456",
            nombre="Fabian",
            apellido="Hoyos"
        )

        # Crear mocks de dependencias mínimas
        from apps.stations.models import Station
        from apps.bikes.models import Bike

        self.estacion = Station.objects.create(
            nombre="Estación Prueba",
            direccion="Calle 10",
            latitud=6.25,
            longitud=-75.56,
        )

        self.bike = Bike.objects.create(
            numero_serie="B123",
            tipo="manual",
            estado="available",
            station=self.estacion
        )

        self.wallet = Wallet.objects.create(usuario=self.usuario, balance=Decimal("50000"))

        self.rental = Rental.objects.create(
            usuario=self.usuario,
            bike=self.bike,
            estacion_origen=self.estacion,
            estado="reservado",
            metodo_pago="wallet",
            costo_estimado=Decimal("10000"),
        )

    # ============================================================
    # 🔹 Caso 1: Cancelación exitosa con wallet
    # ============================================================
    @patch("apps.rentals.services.cancellation_service.CancellationService._enviar_correo_cancelacion")
    @patch("apps.rentals.services.cancellation_service.TransactionService.registrar_movimiento")
    def test_cancelacion_exitosa_wallet(self, mock_transaccion, mock_correo):
        """Debe cancelar una reserva y registrar el reembolso correctamente."""
        result = CancellationService.cancel_reservation(self.usuario, self.rental.id, "Cambio de planes")

        self.rental.refresh_from_db()
        self.assertEqual(self.rental.estado, "cancelado")
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["refunded_amount"], 10000.0)
        mock_transaccion.assert_called_once()
        mock_correo.assert_called_once()

    # ============================================================
    # 🔹 Caso 2: Reserva no pertenece al usuario
    # ============================================================
    def test_cancelacion_usuario_invalido(self):
        """Debe lanzar ValueError si la reserva no pertenece al usuario."""
        User = get_user_model()
        otro_usuario = User.objects.create(email="otro@test.com", password="123456")

        with self.assertRaises(ValueError) as ctx:
            CancellationService.cancel_reservation(otro_usuario, self.rental.id)
        self.assertIn("no pertenece", str(ctx.exception))

    # ============================================================
    # 🔹 Caso 3: Reserva ya iniciada o finalizada
    # ============================================================
    def test_cancelacion_estado_invalido(self):
        """Debe rechazar cancelación si la reserva ya fue iniciada o finalizada."""
        self.rental.estado = "activo"
        self.rental.save()

        with self.assertRaises(ValueError) as ctx:
            CancellationService.cancel_reservation(self.usuario, self.rental.id)
        self.assertIn("no puede ser cancelada", str(ctx.exception))

    # ============================================================
    # 🔹 Caso 4: Reserva con método Stripe (sin reembolso real)
    # ============================================================
    @patch("apps.rentals.services.cancellation_service.CancellationService._enviar_correo_cancelacion")
    def test_cancelacion_stripe_sin_reembolso(self, mock_correo):
        """Debe cancelar correctamente una reserva pagada con Stripe, sin refund local."""
        self.rental.metodo_pago = "stripe"
        self.rental.save()

        result = CancellationService.cancel_reservation(self.usuario, self.rental.id)
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["payment_method"], "stripe")
        mock_correo.assert_called_once()

    # ============================================================
    # 🔹 Caso 5: Error al enviar correo (debe manejarse silenciosamente)
    # ============================================================
    @patch("apps.rentals.services.cancellation_service.EmailMultiAlternatives.send", side_effect=Exception("SMTP Error"))
    @patch("apps.rentals.services.cancellation_service.render_to_string", return_value="<html>ok</html>")
    def test_error_envio_correo(self, mock_render, mock_send):
        """_enviar_correo_cancelacion debe capturar errores de envío sin romper."""
        rental = self.rental
        usuario = self.usuario

        # No debe lanzar excepción aunque el envío falle
        try:
            CancellationService._enviar_correo_cancelacion(usuario, rental, motivo="Falla SMTP")
        except Exception:
            self.fail("No debe lanzar excepción ante fallo de correo")

        mock_render.assert_called_once()
        mock_send.assert_called_once()
