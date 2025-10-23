# apps/transactions/models.py
from django.db import models
from decimal import Decimal
from apps.wallet.models import Wallet


class WalletTransaccion(models.Model):
    TIPOS = [
        ("RECARGA", "Recarga de saldo"),
        ("PAGO", "Pago de viaje o servicio"),
        ("REEMBOLSO", "Reembolso"),
        ("PENALIDAD", "Penalidad por uso indebido"),
        ("AJUSTE", "Ajuste manual"),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transacciones"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Monto positivo (RECARGA) o negativo (PAGO, etc.)"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción libre de la transacción"
    )
    saldo_resultante = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Saldo después de aplicar esta transacción"
    )
    referencia_externa = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Ej: trip_id, payment_intent_id, etc."
    )
    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-creado_en']
        verbose_name = "Transacción de Wallet"
        verbose_name_plural = "Transacciones de Wallet"

    def __str__(self):
        return f"{self.tipo} de {self.monto} COP – {self.wallet.usuario.username}"
