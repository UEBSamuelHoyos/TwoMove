from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.payment.services.stripe_service import crear_setup_intent
from apps.payment.models import MetodoTarjeta


class TestStripeService(TestCase):
    """Pruebas unitarias para el servicio StripeService (crear_setup_intent)."""

    def setUp(self):
        """Crea un usuario base para las pruebas."""
        User = get_user_model()
        self.usuario = User.objects.create(
            email="testuser@example.com",
            password="123456",
            nombre="Fabian",
            apellido="Hoyos"
        )

    # ============================================================
    # 🧩 Caso 1: Usuario ya tiene customer_id
    # ============================================================
    @patch("apps.payment.services.stripe_service.stripe.SetupIntent.create")
    @patch("apps.payment.services.stripe_service.MetodoTarjeta.objects.filter")
    def test_crear_setup_intent_usuario_con_customer(self, mock_filter, mock_create_intent):
        """Debe usar el customer existente si el usuario ya tiene tarjeta con customer_id."""
        # Simular que ya tiene una tarjeta registrada
        metodo_mock = MagicMock()
        metodo_mock.stripe_customer_id = "cus_existente_123"
        mock_filter.return_value.first.return_value = metodo_mock

        mock_create_intent.return_value = MagicMock(id="seti_123", customer="cus_existente_123")

        result = crear_setup_intent(self.usuario)

        mock_create_intent.assert_called_once_with(
            customer="cus_existente_123",
            metadata={"user_id": self.usuario.pk}
        )
        self.assertEqual(result.id, "seti_123")

    # ============================================================
    # 🧩 Caso 2: Usuario sin customer_id → se crea nuevo customer
    # ============================================================
    @patch("apps.payment.services.stripe_service.stripe.SetupIntent.create")
    @patch("apps.payment.services.stripe_service.stripe.Customer.create")
    @patch("apps.payment.services.stripe_service.MetodoTarjeta.objects.filter")
    def test_crear_setup_intent_usuario_sin_customer(self, mock_filter, mock_customer_create, mock_intent_create):
        """Debe crear un nuevo customer en Stripe si el usuario no tiene customer_id."""
        # Simular que no tiene tarjetas asociadas
        mock_filter.return_value.first.return_value = None

        # Mock de creación de Customer
        mock_customer = MagicMock(id="cus_nuevo_999")
        mock_customer_create.return_value = mock_customer

        # Mock de creación de SetupIntent
        mock_intent = MagicMock(id="seti_999", customer="cus_nuevo_999")
        mock_intent_create.return_value = mock_intent

        result = crear_setup_intent(self.usuario)

        # Validar que se creó el Customer y luego el SetupIntent
        mock_customer_create.assert_called_once_with(
            email=self.usuario.email,
            name=f"{self.usuario.nombre} {self.usuario.apellido}"
        )
        mock_intent_create.assert_called_once_with(
            customer="cus_nuevo_999",
            metadata={"user_id": self.usuario.pk}
        )
        self.assertEqual(result.id, "seti_999")

    # ============================================================
    # 🧩 Caso 3: Falla de red o error de Stripe
    # ============================================================
    @patch("apps.payment.services.stripe_service.stripe.Customer.create", side_effect=Exception("Network error"))
    @patch("apps.payment.services.stripe_service.MetodoTarjeta.objects.filter")
    def test_crear_setup_intent_error(self, mock_filter, mock_customer_create):
        """Debe propagar la excepción si Stripe lanza un error."""
        mock_filter.return_value.first.return_value = None
        with self.assertRaises(Exception) as ctx:
            crear_setup_intent(self.usuario)
        self.assertIn("Network error", str(ctx.exception))
