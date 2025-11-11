from decimal import Decimal


class CostoBase:
    """
    Componente base del patrón Decorator.
    Calcula el costo estándar según el tipo de viaje.
    """

    def calcular(self, rental, duracion_min=None, fuera_estacion=False):
        if rental.tipo_viaje == "ultima_milla":
            return Decimal("17500")
        return Decimal("25000")


# -------------------------------------------------------------
# ⏱ Decorador: Costo por tiempo extra
# -------------------------------------------------------------
class CostoPorTiempoExtra:
    """
    Agrega sobrecosto por minutos excedidos del tiempo permitido.
    """
    def __init__(self, componente):
        self._componente = componente

    def calcular(self, rental, duracion_min, fuera_estacion=False):
        costo = self._componente.calcular(rental, duracion_min, fuera_estacion)
        limite = 45 if rental.tipo_viaje == "ultima_milla" else 75

        if duracion_min > limite:
            exceso = duracion_min - limite
            extra = Decimal(exceso) * Decimal("250")
            print(f"⚠️ Exceso de {exceso:.1f} min → +${extra}")
            costo += extra

        return costo


# -------------------------------------------------------------
# 🚲 Decorador: Costo por finalización fuera de estación
# -------------------------------------------------------------
class CostoPorFueraDeEstacion:
    """
    Agrega multa si el viaje termina fuera de una estación registrada.
    """
    def __init__(self, componente):
        self._componente = componente

    def calcular(self, rental, duracion_min, fuera_estacion):
        costo = self._componente.calcular(rental, duracion_min, fuera_estacion)
        if fuera_estacion:
            multa = Decimal("5000")
            print(f"🚨 Multa por finalizar fuera de estación: +${multa}")
            costo += multa
        return costo
