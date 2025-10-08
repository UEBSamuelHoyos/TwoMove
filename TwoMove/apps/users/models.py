from django.db import models
from django.utils import timezone
import random

class Usuario(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('sancionado', 'Sancionado'),
        ('inactivo', 'Inactivo'),
    ]

    usuario_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    contrasena_hash = models.CharField(max_length=255)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='inactivo')
    codigo_verificacion = models.CharField(max_length=6, blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)

    def generar_codigo_verificacion(self):
        self.codigo_verificacion = str(random.randint(100000, 999999))
        self.save()

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"
