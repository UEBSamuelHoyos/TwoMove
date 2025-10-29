from django.db import models

class Bike(models.Model):
    TYPE_CHOICES = [
        ('electric', 'Eléctrica'),
        ('manual', 'Convencional'),
    ]

    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('reserved', 'Reservada'),
        ('in_use', 'En uso'),
        ('maintenance', 'Mantenimiento'),
        ('unavailable', 'No disponible'),
    ]

    numero_serie = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TYPE_CHOICES)
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    # ⚡ Nuevo campo — porcentaje de batería
    bateria_porcentaje = models.PositiveIntegerField(
        default=100,
        help_text="Porcentaje de batería (solo para bicicletas eléctricas)."
    )

    # 🔗 Relación con estación
    station = models.ForeignKey(
        'stations.Station',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bikes'
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.numero_serie} - {self.get_tipo_display()} ({self.estado})"

    class Meta:
        verbose_name = "Bicicleta"
        verbose_name_plural = "Bicicletas"
