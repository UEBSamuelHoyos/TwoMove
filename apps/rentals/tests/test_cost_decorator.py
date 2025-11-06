from decimal import Decimal
from django.test import TestCase

from apps.rentals.services.cost_decorator import (
    CostoBase,
    CostoPorTiempoExtra,
    CostoPorFueraDeEstacion,
)


class DummyRental:
    """Objeto simulado para representar una reserva (rental) en los tests."""
    def __init__(self, tipo_viaje):
        self.tipo_viaje = tipo_viaje


class TestCostDecorator(TestCase):
    """Pruebas unitarias para los componentes y decoradores de costo de viaje."""

    def setUp(self):
        self.rental_ultima_milla = DummyRental("ultima_milla")
        self.rental_recorrido_largo = DummyRental("recorrido_largo")

    # ============================================================
    # 🔹 Costo base
    # ============================================================
    def test_costo_base_ultima_milla(self):
        """Debe devolver 17500 para viajes tipo 'ultima_milla'."""
        costo = CostoBase().calcular(self.rental_ultima_milla)
        self.assertEqual(costo, Decimal("17500"))

    def test_costo_base_recorrido_largo(self):
        """Debe devolver 25000 para viajes tipo 'recorrido_largo'."""
        costo = CostoBase().calcular(self.rental_recorrido_largo)
        self.assertEqual(costo, Decimal("25000"))

    # ============================================================
    # ⏱ Decorador: Costo por tiempo extra
    # ============================================================
    def test_costo_por_tiempo_extra_dentro_limite(self):
        """Si la duración está dentro del límite, no debe aumentar el costo."""
        base = CostoBase()
        decorador = CostoPorTiempoExtra(base)

        costo = decorador.calcular(self.rental_ultima_milla, duracion_min=40)
        self.assertEqual(costo, Decimal("17500"))

    def test_costo_por_tiempo_extra_fuera_limite(self):
        """Debe sumar $250 por cada minuto extra en 'ultima_milla'."""
        base = CostoBase()
        decorador = CostoPorTiempoExtra(base)

        costo = decorador.calcular(self.rental_ultima_milla, duracion_min=50)
        # 5 minutos extra → 5 * 250 = 1250 + 17500 = 18750
        self.assertEqual(costo, Decimal("18750"))

    def test_costo_por_tiempo_extra_largo(self):
        """Debe usar límite de 75 min para 'recorrido_largo'."""
        base = CostoBase()
        decorador = CostoPorTiempoExtra(base)

        costo = decorador.calcular(self.rental_recorrido_largo, duracion_min=80)
        # 5 minutos extra → 5 * 250 = 1250 + 25000 = 26250
        self.assertEqual(costo, Decimal("26250"))

    # ============================================================
    # 🚲 Decorador: Costo por finalización fuera de estación
    # ============================================================
    def test_costo_fuera_estacion(self):
        """Debe sumar $5000 si el viaje termina fuera de estación."""
        base = CostoBase()
        decorador = CostoPorFueraDeEstacion(base)

        costo = decorador.calcular(self.rental_ultima_milla, duracion_min=30, fuera_estacion=True)
        self.assertEqual(costo, Decimal("22500"))  # 17500 + 5000

    def test_costo_dentro_estacion(self):
        """No debe agregar multa si el viaje termina dentro de una estación."""
        base = CostoBase()
        decorador = CostoPorFueraDeEstacion(base)

        costo = decorador.calcular(self.rental_ultima_milla, duracion_min=30, fuera_estacion=False)
        self.assertEqual(costo, Decimal("17500"))

    # ============================================================
    # 🧩 Decoradores combinados
    # ============================================================
    def test_combinacion_tiempo_extra_y_fuera_estacion(self):
        """Debe aplicar ambos decoradores correctamente en combinación."""
        base = CostoBase()
        decorador = CostoPorFueraDeEstacion(CostoPorTiempoExtra(base))

        costo = decorador.calcular(self.rental_ultima_milla, duracion_min=50, fuera_estacion=True)
        # Base 17500 + (5 * 250 = 1250) + multa 5000 = 23750
        self.assertEqual(costo, Decimal("23750"))
