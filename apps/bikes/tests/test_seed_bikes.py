from django.test import TestCase
from django.db import transaction
from apps.bikes.models import Bike
from apps.stations.models import Station
from apps.bikes.services.seed_bikes import seed_bikes


class TestSeedBikes(TestCase):
    """
    Pruebas unitarias para el script seed_bikes.py.
    Verifica la creación y actualización de bicicletas asociadas a estaciones.
    """

    def test_seed_bikes_sin_estaciones(self):
        """Debe mostrar advertencia si no hay estaciones creadas."""
        Bike.objects.all().delete()
        Station.objects.all().delete()

        from io import StringIO
        import sys

        # Capturar salida
        salida = StringIO()
        sys_stdout_original = sys.stdout
        sys.stdout = salida

        seed_bikes()

        sys.stdout = sys_stdout_original
        output = salida.getvalue()

        self.assertIn("No hay estaciones creadas", output)
        self.assertEqual(Bike.objects.count(), 0)

    def test_seed_bikes_con_estaciones(self):
        """Debe crear 8 bicicletas por estación (4 eléctricas y 4 mecánicas)."""
        Station.objects.all().delete()
        Bike.objects.all().delete()

        s1 = Station.objects.create(nombre="Estación Norte", direccion="Calle 1")
        s2 = Station.objects.create(nombre="Estación Sur", direccion="Calle 2")

        with transaction.atomic():
            seed_bikes()

        bikes = Bike.objects.all()
        self.assertEqual(bikes.count(), 16)  # 2 estaciones × 8 bicicletas cada una

        # Validar por tipo
        electricas = bikes.filter(tipo="electric").count()
        manuales = bikes.filter(tipo="manual").count()
        self.assertEqual(electricas, 8)
        self.assertEqual(manuales, 8)

        # Validar campos
        for bike in bikes:
            self.assertIsNotNone(bike.station)
            self.assertEqual(bike.estado, "available")
            self.assertTrue(60 <= bike.bateria_porcentaje <= 100)
            self.assertTrue(bike.numero_serie.startswith(("E-", "M-")))

        # Verificar que no se dupliquen
        seed_bikes()
        self.assertEqual(Bike.objects.count(), 16)

    def test_seed_bikes_actualiza_existentes(self):
        """Debe actualizar baterías sin duplicar registros existentes."""
        Station.objects.all().delete()
        Bike.objects.all().delete()

        station = Station.objects.create(nombre="Estación Única", direccion="Carrera 10")
        seed_bikes()

        initial_bikes = list(Bike.objects.values_list("numero_serie", "bateria_porcentaje"))
        seed_bikes()  # vuelve a ejecutar (debe actualizar, no duplicar)

        final_bikes = list(Bike.objects.values_list("numero_serie", "bateria_porcentaje"))

        # Mismo número de registros
        self.assertEqual(Bike.objects.count(), 8)

        # Los seriales son iguales
        initial_serials = {b[0] for b in initial_bikes}
        final_serials = {b[0] for b in final_bikes}
        self.assertEqual(initial_serials, final_serials)
