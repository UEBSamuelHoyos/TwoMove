from django.db import models
from django.utils import timezone
from decimal import Decimal


class Rental(models.Model):
    TIPO_VIAJE = [
        ('ultima_milla', 'Última Milla'),
        ('recorrido_largo', 'Recorrido Largo'),
    ]

    ESTADO = [
        ('reservado', 'Reservado'),
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey('users.Usuario', on_delete=models.CASCADE)
    bike = models.ForeignKey('bikes.Bike', on_delete=models.CASCADE)
    estacion_origen = models.ForeignKey('stations.Station', related_name='viajes_salida', on_delete=models.CASCADE)
    estacion_destino = models.ForeignKey('stations.Station', related_name='viajes_llegada', null=True, blank=True, on_delete=models.SET_NULL)

    tipo_viaje = models.CharField(max_length=20, choices=TIPO_VIAJE, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='reservado')
    metodo_pago = models.CharField(max_length=20, null=True, blank=True)  # 👈 nuevo

    fecha_reserva = models.DateField(null=True, blank=True)  # 👈 nuevo
    hora_reserva = models.TimeField(null=True, blank=True)   # 👈 nuevo

    hora_inicio = models.DateTimeField(null=True, blank=True)
    hora_fin = models.DateTimeField(null=True, blank=True)
    duracion_minutos = models.PositiveIntegerField(null=True, blank=True)

    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 👈 nuevo
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # 🔐 Información adicional para el usuario
    bike_serial_reservada = models.CharField(max_length=100, blank=True, null=True)
    bike_dock_reservado = models.CharField(max_length=50, blank=True, null=True)
    codigo_desbloqueo = models.CharField(max_length=10, blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def calcular_costo(self):
        """
        Calcula el costo total basado en el tipo de viaje y la duración (minutos).
        """
        if self.tipo_viaje == 'ultima_milla':
            base, limite, extra = Decimal('17500'), 45, Decimal('250')
        else:
            base, limite, extra = Decimal('25000'), 75, Decimal('1000')

        if not self.duracion_minutos:
            return base

        excedente = max(0, self.duracion_minutos - limite)
        return base + (excedente * extra)

    def __str__(self):
        return f"Reserva #{self.id} - {self.usuario.email} ({self.estado})"
