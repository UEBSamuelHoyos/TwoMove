# apps/transactions/services/transaction_service.py
from decimal import Decimal
from django.db import transaction
from apps.transactions.models import WalletTransaccion


class TransactionService:
    """
    Servicio central para registrar movimientos en la wallet.
    Maneja el signo, tipos de operación y actualización del saldo de forma segura.
    """

    @staticmethod
    @transaction.atomic
    def registrar_movimiento(wallet, tipo, monto: Decimal, descripcion=""):
        # Validar tipo
        if tipo not in dict(WalletTransaccion.TIPOS):
            raise ValueError(f"Tipo de transacción no válido: {tipo}")

        # Normalizar monto (asegurar que siempre sea positivo internamente)
        monto = abs(monto)

        # Determinar el signo según el tipo
        if tipo in ("PAGO", "PENALIDAD"):
            monto_final = -monto
        elif tipo in ("RECARGA", "REEMBOLSO", "AJUSTE"):
            monto_final = monto
        else:
            raise ValueError(f"Tipo de movimiento desconocido: {tipo}")

        # Validar fondos en caso de débito
        if monto_final < 0 and wallet.balance + monto_final < 0:
            raise ValueError("Saldo insuficiente en la wallet para realizar esta operación.")

        # Calcular nuevo saldo
        nuevo_saldo = wallet.balance + monto_final

        # Registrar la transacción
        transaccion = WalletTransaccion.objects.create(
            wallet=wallet,
            tipo=tipo,
            monto=monto_final,
            descripcion=descripcion,
            saldo_resultante=nuevo_saldo
        )

        # Actualizar balance de wallet
        wallet.balance = nuevo_saldo
        wallet.save(update_fields=["balance"])

        print(f"💰 [{tipo}] {monto_final} COP → Nuevo saldo: {nuevo_saldo} (Usuario: {wallet.usuario.email})")

        return transaccion
