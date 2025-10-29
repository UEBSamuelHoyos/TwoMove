from django.db import models

class Station(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=255)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Capacidad separada por tipo
    capacidad_electricas = models.PositiveIntegerField(default=10)
    capacidad_mecanicas = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.nombre

    # Propiedades útiles para el sistema
    @property
    def disponibles_electricas(self):
        """Cantidad de bicicletas eléctricas disponibles en esta estación"""
        return self.bikes.filter(tipo='electric', estado='available').count()

    @property
    def disponibles_mecanicas(self):
        """Cantidad de bicicletas mecánicas disponibles en esta estación"""
        return self.bikes.filter(tipo='manual', estado='available').count()

    @property
    def total_disponibles(self):
        """Total de bicicletas disponibles (sumando ambos tipos)"""
        return self.disponibles_electricas + self.disponibles_mecanicas
