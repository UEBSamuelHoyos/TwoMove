from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.rentals.services.reservation_service import ReservationService
from apps.rentals.models import Rental
from apps.bikes.models import Bike
from apps.stations.models import Station
from apps.wallet.models import Wallet
from apps.payment.models import MetodoTarjeta
from apps.transactions.models import WalletTransaccion


class TestReservationService(TestCase):
    """Pruebas unitarias para el flujo de ReservationService."""

    def setUp(self):
        Usuario = get_user_model()
        self.usuario = Usuario.objects.create_user(
            email="usuario@test.com",
            password="123456",
            nombre="Fabian",
            apellido="Hoyos"
        )

        # Crear estaciones
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

        # Bicicleta disponible
        self.bike = Bike.objects.create(
            numero_serie="B-123",
            tipo="electric",
            estado="available",
            station=self.origen,
            bateria_porcentaje=90,
        )

        # Wallet con saldo
        self.wallet = Wallet.objects.create(usuario=self.usuario, balance=Decimal("50000"))

        # Tarjeta registrada
        self.tarjeta = MetodoTarjeta.objects.create(
            usuario=self.usuario,
            stripe_payment_method_id="pm_123",
            stripe_customer_id="cus_123",
            brand="visa",
            last4="4242",
            exp_month=12,
            exp_year=2030,
        )

    # ============================================================
    # 🔹 Caso exitoso con wallet
    # ============================================================
    @patch("apps.rentals.services.reservation_service.EmailMultiAlternatives")
    def test_crear_reserva_con_wallet(self, mock_email):
        """Debe crear una reserva con método wallet y descontar saldo."""
        mock_email.return_value.send.return_value = True

        rental = ReservationService.create_reservation(
            usuario=self.usuario,
            estacion_origen_id=self.origen.id,
            tipo_bicicleta="electric",
            tipo_viaje="ultima_milla",
            metodo_pago="wallet",
            estacion_destino_id=self.destino.id
        )

        self.assertIsInstance(rental, Rental)
        self.assertEqual(rental.estado, "reservado")
        self.assertEqual(Bike.objects.get(id=self.bike.id).estado, "reserved")

        wallet_actual = Wallet.objects.get(usuario=self.usuario)
        self.assertLess(wallet_actual.balance, Decimal("50000"))
        self.assertTrue(WalletTransaccion.objects.filter(wallet=self.wallet).exists())

    # ============================================================
    # 🔹 Caso exitoso con tarjeta
    # ============================================================
    @patch("apps.rentals.services.reservation_service.EmailMultiAlternatives")
    def test_crear_reserva_con_tarjeta(self, mock_email):
        """Debe crear una reserva usando tarjeta registrada."""
        mock_email.return_value.send.return_value = True

        rental = ReservationService.create_reservation(
            usuario=self.usuario,
            estacion_origen_id=self.origen.id,
            tipo_bicicleta="electric",
            tipo_viaje="recorrido_largo",
            metodo_pago="card",
            estacion_destino_id=self.destino.id
        )
        self.assertIsInstance(rental, Rental)
        self.assertEqual(rental.metodo_pago, "card")
        self.assertEqual(rental.estacion_destino, self.destino)

    # ============================================================
    # ⚠️ Validaciones de error
    # ============================================================
    def test_reserva_con_usuario_con_multas(self):
        """Debe impedir reservas si el usuario tiene multas activas."""
        self.usuario.tiene_multas = True
        with self.assertRaises(ValidationError):
            ReservationService.create_reservation(
                usuario=self.usuario,
                estacion_origen_id=self.origen.id,
                tipo_bicicleta="manual",
                tipo_viaje="ultima_milla",
                metodo_pago="wallet",
                estacion_destino_id=self.destino.id
            )

    def test_reserva_sin_bicicletas_disponibles(self):
        """Debe fallar si no hay bicicletas disponibles."""
        Bike.objects.all().update(estado="reserved")
        with self.assertRaises(ValidationError):
            ReservationService.create_reservation(
                usuario=self.usuario,
                estacion_origen_id=self.origen.id,
                tipo_bicicleta="manual",
                tipo_viaje="ultima_milla",
                metodo_pago="wallet",
                estacion_destino_id=self.destino.id
            )

    def test_reserva_sin_wallet_suficiente(self):
        """Debe lanzar error si el saldo es insuficiente."""
        self.wallet.balance = Decimal("1000")
        self.wallet.save()
        with self.assertRaises(ValidationError):
            ReservationService.create_reservation(
                usuario=self.usuario,
                estacion_origen_id=self.origen.id,
                tipo_bicicleta="electric",
                tipo_viaje="ultima_milla",
                metodo_pago="wallet",
                estacion_destino_id=self.destino.id
            )

    def test_reserva_sin_tarjeta_registrada(self):
        """Debe lanzar error si no tiene tarjeta al usar método card."""
        MetodoTarjeta.objects.all().delete()
        with self.assertRaises(ValidationError):
            ReservationService.create_reservation(
                usuario=self.usuario,
                estacion_origen_id=self.origen.id,
                tipo_bicicleta="electric",
                tipo_viaje="ultima_milla",
                metodo_pago="card",
                estacion_destino_id=self.destino.id
            )

    def test_estaciones_iguales(self):
        """Debe impedir reservar si origen y destino son la misma estación."""
        with self.assertRaises(ValidationError):
            ReservationService.create_reservation(
                usuario=self.usuario,
                estacion_origen_id=self.origen.id,
                tipo_bicicleta="electric",
                tipo_viaje="ultima_milla",
                metodo_pago="wallet",
                estacion_destino_id=self.origen.id
            )
