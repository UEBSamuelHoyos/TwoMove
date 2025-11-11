from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.wallet.models import Wallet
from apps.wallet.services.wallet_service import WalletService


class TestWalletService(TestCase):
    """
    🔹 Pruebas unitarias para WalletService (según el modelo actual sin métodos extra).
    Valida la creación, obtención y actualización de saldos mediante la capa de servicio.
    """

    def setUp(self):
        Usuario = get_user_model()
        self.usuario = Usuario.objects.create_user(
            email="usuario@test.com",
            password="123456",
            nombre="Fabian",
            apellido="Hoyos"
        )

    # ============================================================
    # ✅ Caso 1: obtener_o_crear_wallet crea nueva si no existe
    # ============================================================
    def test_obtener_o_crear_wallet_crea_nueva(self):
        """Debe crear una wallet si el usuario no tiene una."""
        self.assertFalse(Wallet.objects.filter(usuario=self.usuario).exists())
        wallet = WalletService.obtener_o_crear_wallet(self.usuario)

        self.assertIsInstance(wallet, Wallet)
        self.assertEqual(wallet.usuario, self.usuario)
        self.assertEqual(wallet.balance, Decimal("0"))
        self.assertEqual(Wallet.objects.count(), 1)

    # ============================================================
    # ✅ Caso 2: obtener_o_crear_wallet reutiliza la existente
    # ============================================================
    def test_obtener_o_crear_wallet_reutiliza_existente(self):
        """Debe retornar la misma wallet si ya existe."""
        w1 = WalletService.obtener_o_crear_wallet(self.usuario)
        w2 = WalletService.obtener_o_crear_wallet(self.usuario)
        self.assertEqual(w1.id, w2.id)
        self.assertEqual(Wallet.objects.count(), 1)

    # ============================================================
    # ✅ Caso 3: actualizar saldo manualmente
    # ============================================================
    def test_actualizar_saldo_manual(self):
        """Debe poder actualizar el saldo usando el método del modelo."""
        wallet = WalletService.obtener_o_crear_wallet(self.usuario)
        wallet.actualizar_saldo(Decimal("25000"))
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("25000"))

    # ============================================================
    # ⚠️ Caso 4: agregar_saldo o descontar_saldo no existen
    # ============================================================
    def test_wallet_service_agregar_y_descontar_no_implementados(self):
        """
        Dado que el modelo actual no tiene los métodos agregar_saldo ni descontar_saldo,
        el servicio debe lanzar AttributeError al intentar usarlos.
        """
        wallet = WalletService.obtener_o_crear_wallet(self.usuario)
        with self.assertRaises(AttributeError):
            WalletService.agregar_saldo(self.usuario, Decimal("10000"))

        with self.assertRaises(AttributeError):
            WalletService.descontar_saldo(self.usuario, Decimal("5000"))

    # ============================================================
    # ✅ Caso 5: comportamiento consistente con balance
    # ============================================================
    def test_crea_wallet_con_balance_default(self):
        """Verifica que las wallets nuevas se creen con balance 0."""
        wallet = WalletService.obtener_o_crear_wallet(self.usuario)
        self.assertEqual(wallet.balance, Decimal("0"))
