from django.db import models
from django.utils import timezone


class BikeTelemetry(models.Model):
    """
    Representa un paquete de datos enviado por una bicicleta IoT
    (posición GPS, batería, estado de candado, timestamp).
    """

    bike_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(default=timezone.now)

    latitude = models.FloatField()
    longitude = models.FloatField()

    battery = models.FloatField(help_text="Porcentaje de batería (0–100%)")
    lock_status = models.CharField(max_length=20, choices=[
        ("LOCKED", "Candado cerrado"),
        ("UNLOCKED", "Candado abierto"),
    ])

    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at"]
        verbose_name = "Telemetría de Bicicleta"
        verbose_name_plural = "Telemetrías de Bicicletas"

    def __str__(self):
        return f"Bike {self.bike_id} @ {self.latitude:.4f}, {self.longitude:.4f} ({self.lock_status})"
