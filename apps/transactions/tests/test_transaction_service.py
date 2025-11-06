from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.wallet.models import Wallet
from apps.transactions.models import WalletTransaccion
from apps.transactions.services.transaction_service import TransactionService


class TestTransactionService(TestCase):
    """
    🔹 Pruebas unitarias para TransactionService.
    Verifica los diferentes tipos de movimientos y control de saldo.
    """

    def setUp(self):
        Usuario = get_user_model()
        self.usuario = Usuario.objects.create_user(
            email="usuario@test.com",
            password="123456",
            nombre="Fabian",
            apellido="Hoyos"
        )
        self.wallet = Wallet.objects.create(usuario=self.usuario, balance=Decimal("50000"))

    # ============================================================
    # ✅ Caso 1: Recarga (saldo aumenta)
    # ============================================================
    def test_registrar_recarga(self):
        """Debe registrar una recarga y aumentar el saldo."""
        tx = TransactionService.registrar_movimiento(
            wallet=self.wallet,
            tipo="RECARGA",
            monto=Decimal("10000"),
            descripcion="Recarga inicial"
        )

        self.wallet.refresh_from_db()
        self.assertEqual(tx.monto, Decimal("10000"))
        self.assertEqual(tx.tipo, "RECARGA")
        self.assertEqual(self.wallet.balance, Decimal("60000"))
        self.assertEqual(tx.saldo_resultante, self.wallet.balance)

    # ============================================================
    # ✅ Caso 2: Pago (saldo disminuye)
    # ============================================================
    def test_registrar_pago(self):
        """Debe registrar un pago y disminuir el saldo."""
        tx = TransactionService.registrar_movimiento(
            wallet=self.wallet,
            tipo="PAGO",
            monto=Decimal("15000"),
            descripcion="Pago de viaje"
        )

        self.wallet.refresh_from_db()
        self.assertEqual(tx.monto, Decimal("-15000"))
        self.assertEqual(tx.tipo, "PAGO")
        self.assertEqual(self.wallet.balance, Decimal("35000"))

    # ============================================================
    # ✅ Caso 3: Penalidad (multas)
    # ============================================================
    def test_registrar_penalidad(self):
        """Debe registrar una penalidad como débito negativo."""
        tx = TransactionService.registrar_movimiento(
            wallet=self.wallet,
            tipo="PENALIDAD",
            monto=Decimal("5000"),
            descripcion="Multa por mal estacionamiento"
        )

        self.wallet.refresh_from_db()
        self.assertEqual(tx.monto, Decimal("-5000"))
        self.assertEqual(tx.tipo, "PENALIDAD")
        self.assertEqual(self.wallet.balance, Decimal("45000"))

    # ============================================================
    # ✅ Caso 4: Reembolso o ajuste (positivo)
    # ============================================================
    def test_registrar_reembolso(self):
        """Debe registrar un reembolso como crédito positivo."""
        tx = TransactionService.registrar_movimiento(
            wallet=self.wallet,
            tipo="REEMBOLSO",
            monto=Decimal("8000"),
            descripcion="Devolución parcial"
        )

        self.wallet.refresh_from_db()
        self.assertEqual(tx.monto, Decimal("8000"))
        self.assertEqual(tx.tipo, "REEMBOLSO")
        self.assertEqual(self.wallet.balance, Decimal("58000"))

    # ============================================================
    # ⚠️ Caso 5: Saldo insuficiente
    # ============================================================
    def test_saldo_insuficiente_lanza_error(self):
        """Debe lanzar error si no hay fondos suficientes para un pago."""
        with self.assertRaises(ValueError):
            TransactionService.registrar_movimiento(
                wallet=self.wallet,
                tipo="PAGO",
                monto=Decimal("999999"),
                descripcion="Intento de débito sin saldo"
            )

    # ============================================================
    # ⚠️ Caso 6: Tipo inválido
    # ============================================================
    def test_tipo_invalido_lanza_error(self):
        """Debe lanzar error si el tipo de transacción no es válido."""
        with self.assertRaises(ValueError):
            TransactionService.registrar_movimiento(
                wallet=self.wallet,
                tipo="INVALIDO",
                monto=Decimal("1000"),
                descripcion="Tipo inválido"
            )

    # ============================================================
    # ✅ Caso 7: Mantiene consistencia de saldo en múltiples transacciones
    # ============================================================
    def test_movimientos_en_cadena(self):
        """Verifica que los saldos sean consistentes tras varias operaciones."""
        TransactionService.registrar_movimiento(self.wallet, "RECARGA", Decimal("10000"))
        TransactionService.registrar_movimiento(self.wallet, "PAGO", Decimal("5000"))
        TransactionService.registrar_movimiento(self.wallet, "REEMBOLSO", Decimal("2000"))

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("57000"))
        self.assertEqual(WalletTransaccion.objects.count(), 3)
