# apps/transactions/services/transaction_service.py
from apps.transactions.models import WalletTransaccion
from decimal import Decimal

class TransactionService:

    @staticmethod
    def registrar_movimiento(wallet, tipo, monto: Decimal, descripcion=""):
        if tipo == "PAGO" and wallet.balance < monto:
            raise ValueError("Saldo insuficiente")

        # Calcula el saldo resultante
        saldo_resultante = wallet.balance + monto if tipo == "RECARGA" else wallet.balance - monto

        # Registra la transacción en DB
        transaccion = WalletTransaccion.objects.create(
            wallet=wallet,
            tipo=tipo,
            monto=monto if tipo=="RECARGA" else -monto,
            descripcion=descripcion,
            saldo_resultante=saldo_resultante
        )

        # Actualiza el balance del wallet
        wallet.balance = saldo_resultante
        wallet.save()

        # Aquí puedes registrar también en Stripe (metadata u otra tabla)
        # Ej: transaccion.stripe_id = "pi_xxxx"
        # transaccion.save()

        return transaccion
