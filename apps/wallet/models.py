from django.db import models
from django.conf import settings
from decimal import Decimal


class Wallet(models.Model):
    """
    Modelo que representa la billetera de un usuario.
    Contiene únicamente el balance disponible y la relación con el usuario.
    Las transacciones se registran en apps.transactions.models.WalletTransaccion.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Saldo disponible en la billetera"
    )

    # Futuro: para preautorizar cobros sin descontar aún
    # saldo_bloqueado = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Billetera de {self.usuario.email} - Saldo: {self.balance} COP"

    def actualizar_saldo(self, nuevo_balance):
        """
        Actualiza el balance de forma manual (evitar usar si hay transacciones).
        """
        self.balance = Decimal(nuevo_balance)
        self.save()
