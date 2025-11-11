from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model

from stripe import CardError, InvalidRequestError, APIConnectionError  # ✅ Import correcto

from apps.payment.services.recargar_saldo_service import RecargarSaldoService
from apps.payment.models import MetodoTarjeta
from apps.wallet.models import Wallet


class TestRecargarSaldoService(TestCase):
    """Pruebas unitarias para el servicio RecargarSaldoService."""

    def setUp(self):
        """Crea un usuario y una tarjeta simulada antes de cada test."""
        User = get_user_model()
        self.usuario = User.objects.create(
            email="testuser@example.com",
            password="123456"
        )

        self.metodo = MetodoTarjeta.objects.create(
            usuario=self.usuario,
            stripe_payment_method_id="pm_test_123",
            stripe_customer_id="cus_test_456",
            brand="visa",
            last4="4242",
            exp_month=12,
            exp_year=2030
        )

    # ============================================================
    # 🔹 TEST: Método de pago correcto
    # ============================================================
    def test_obtener_metodo_pago_valido(self):
        service = RecargarSaldoService(usuario=self.usuario, amount=Decimal("100.00"))
        metodo = service.obtener_metodo_pago()
        self.assertEqual(metodo.stripe_payment_method_id, "pm_test_123")

    def test_obtener_metodo_pago_inexistente(self):
        MetodoTarjeta.objects.all().delete()
        service = RecargarSaldoService(usuario=self.usuario, amount=Decimal("100.00"))
        with self.assertRaises(Exception) as ctx:
            service.obtener_metodo_pago()
        self.assertIn("No se encontró una tarjeta válida", str(ctx.exception))

    def test_obtener_metodo_pago_sin_customer(self):
        self.metodo.stripe_customer_id = None
        self.metodo.save()
        service = RecargarSaldoService(usuario=self.usuario, amount=Decimal("100.00"))
        with self.assertRaises(Exception) as ctx:
            service.obtener_metodo_pago()
        self.assertIn("no tiene un cliente", str(ctx.exception))

    # ============================================================
    # 💳 TEST: Crear PaymentIntent exitoso
    # ============================================================
    @patch("apps.payment.services.recargar_saldo_service.stripe.PaymentIntent.create")
    @patch("apps.payment.services.recargar_saldo_service.TransactionService.registrar_movimiento")
    def test_crear_payment_intent_exitoso(self, mock_transaccion, mock_stripe_create):
        mock_stripe_create.return_value = MagicMock(
            id="pi_test_123",
            status="succeeded",
            currency="cop",
            created=1234567890
        )

        service = RecargarSaldoService(usuario=self.usuario, amount=Decimal("150.50"))
        result = service.crear_payment_intent()

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["currency"], "COP")
        mock_transaccion.assert_called_once()

    # ============================================================
    # ❌ TEST: Manejo de errores de Stripe
    # ============================================================
    @patch("apps.payment.services.recargar_saldo_service.stripe.PaymentIntent.create")
    def test_crear_payment_intent_card_error(self, mock_stripe_create):
        mock_stripe_create.side_effect = CardError("Card declined", None, None)

        service = RecargarSaldoService(usuario=self.usuario, amount=Decimal("100.00"))
        with self.assertRaises(Exception) as ctx:
            service.crear_payment_intent()
        self.assertIn("Error de tarjeta", str(ctx.exception))

    @patch("apps.payment.services.recargar_saldo_service.stripe.PaymentIntent.create")
    def test_crear_payment_intent_invalid_request(self, mock_stripe_create):
        mock_stripe_create.side_effect = InvalidRequestError("Invalid request", "param")

        service = RecargarSaldoService(usuario=self.usuario, amount=Decimal("100.00"))
        with self.assertRaises(Exception) as ctx:
            service.crear_payment_intent()
        self.assertIn("Error de solicitud", str(ctx.exception))

    @patch("apps.payment.services.recargar_saldo_service.stripe.PaymentIntent.create")
    def test_crear_payment_intent_api_connection(self, mock_stripe_create):
        mock_stripe_create.side_effect = APIConnectionError("Network error")

        service = RecargarSaldoService(usuario=self.usuario, amount=Decimal("100.00"))
        with self.assertRaises(Exception) as ctx:
            service.crear_payment_intent()
        self.assertIn("Error de conexión", str(ctx.exception))
