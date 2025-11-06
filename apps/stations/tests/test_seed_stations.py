import os
import sys
import io
from django.test import TestCase
from django.conf import settings
from contextlib import redirect_stdout

# Asegurar que el entorno Django esté inicializado igual que el script original
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TwoMove.settings")

from apps.stations.models import Station
from apps.stations.services import seed_stations  # Importa el módulo, no la función


class TestSeedStations(TestCase):
    """
    🔹 Pruebas unitarias para el script seed_stations.py
    Verifica creación, no duplicación y consistencia de datos.
    """

    def setUp(self):
        Station.objects.all().delete()

    # ============================================================
    # ✅ Caso 1: Crea las 50 estaciones si no existen
    # ============================================================
    def test_seed_crea_50_estaciones(self):
        """Debe crear 50 estaciones si la tabla está vacía."""
        self.assertEqual(Station.objects.count(), 0)

        f = io.StringIO()
        with redirect_stdout(f):
            seed_stations.seed_stations()
        salida = f.getvalue()

        # Verifica mensaje y cantidad
        self.assertIn("✅ Se han creado o actualizado 50 estaciones correctamente.", salida)
        self.assertEqual(Station.objects.count(), 50)

    # ============================================================
    # ✅ Caso 2: No duplica estaciones si ya existen
    # ============================================================
    def test_seed_no_duplica_estaciones_existentes(self):
        """Si el seed se ejecuta dos veces, no debe duplicar las estaciones."""
        seed_stations.seed_stations()
        cantidad_inicial = Station.objects.count()

        f = io.StringIO()
        with redirect_stdout(f):
            seed_stations.seed_stations()
        salida = f.getvalue()

        self.assertIn("✅ Se han creado o actualizado 50 estaciones correctamente.", salida)
        self.assertEqual(Station.objects.count(), cantidad_inicial)

    # ============================================================
    # ✅ Caso 3: Validar estructura de una estación creada
    # ============================================================
    def test_estaciones_tienen_campos_correctos(self):
        """Cada estación creada debe tener todos los campos esperados."""
        seed_stations.seed_stations()
        estacion = Station.objects.first()

        self.assertIsNotNone(estacion)
        self.assertTrue(estacion.nombre.startswith("Estación"))
        self.assertIn("Bogotá", estacion.direccion)
        self.assertIsNotNone(estacion.latitud)
        self.assertIsNotNone(estacion.longitud)
        self.assertGreater(estacion.capacidad_electricas, 0)
        self.assertGreater(estacion.capacidad_mecanicas, 0)

    # ============================================================
    # ✅ Caso 4: Método __str__
    # ============================================================
    def test_str_devuelve_nombre(self):
        """El método __str__ debe devolver el nombre de la estación."""
        seed_stations.seed_stations()
        estacion = Station.objects.first()
        self.assertEqual(str(estacion), estacion.nombre)
