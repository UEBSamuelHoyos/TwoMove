from django.db import models
from django.conf import settings

class MetodoTarjeta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tarjetas')
    stripe_payment_method_id = models.CharField(max_length=100, unique=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)  # <-- 👈 AÑADIR
    brand = models.CharField(max_length=50)
    last4 = models.CharField(max_length=4)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} ****{self.last4} ({self.usuario})"

