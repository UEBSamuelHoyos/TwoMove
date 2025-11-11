import io
from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone

from apps.admin_dashboard.services.report_service import ReportService
from apps.rentals.models import Rental
from apps.bikes.models import Bike
from apps.users.models import Usuario
from apps.stations.models import Station


class TestReportService(TestCase):
    """Pruebas unitarias para el servicio de reportes administrativos (ReportService)."""

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="testuser@example.com",
            nombre="Fabian",
            apellido="Hoyos",
            password="12345"
        )
        # ✅ Crear estación y bicicleta válidas sin campo 'ciudad'
        self.estacion = Station.objects.create(
            nombre="Estación Central",
            direccion="Calle 1 #2-3"
        )
        self.bike = Bike.objects.create(
            tipo="manual",
            estado="disponible"
        )

    def crear_rentals_finalizados(self):
        now = timezone.now()
        r1 = Rental.objects.create(
            usuario=self.usuario,
            bike=self.bike,
            estacion_origen=self.estacion,
            estacion_destino=self.estacion,
            estado="finalizado",
            hora_inicio=now - timedelta(minutes=30),
            hora_fin=now,
            costo_total=Decimal("100.50")
        )
        r2 = Rental.objects.create(
            usuario=self.usuario,
            bike=self.bike,
            estacion_origen=self.estacion,
            estacion_destino=self.estacion,
            estado="finalizado",
            hora_inicio=now - timedelta(minutes=45),
            hora_fin=now - timedelta(minutes=15),
            costo_total=Decimal("50.00")
        )
        return [r1, r2]

    def test_resumen_general_con_datos(self):
        self.crear_rentals_finalizados()
        result = ReportService.resumen_general()

        self.assertEqual(result["total_viajes"], 2)
        self.assertEqual(result["total_usuarios"], 1)
        self.assertEqual(result["total_recaudado"], Decimal("150.50"))
        self.assertGreater(result["promedio_duracion"], 0)
        self.assertAlmostEqual(result["co2_ev"], 0.6, places=1)

    def test_resumen_general_sin_datos(self):
        result = ReportService.resumen_general()
        self.assertEqual(result["total_viajes"], 0)
        self.assertEqual(result["total_usuarios"], 0)
        self.assertEqual(result["total_recaudado"], 0)
        self.assertEqual(result["promedio_duracion"], 0)
        self.assertEqual(result["co2_ev"], 0.0)

    def test_reporte_por_usuario_existente(self):
        self.crear_rentals_finalizados()
        result = ReportService.reporte_por_usuario(self.usuario.usuario_id)


        self.assertEqual(result["usuario"], self.usuario)
        self.assertEqual(result["total_viajes"], 2)
        self.assertEqual(result["total_gasto"], Decimal("150.50"))
        self.assertGreater(result["promedio_duracion"], 0)
        self.assertTrue(list(result["viajes"]))

    def test_reporte_por_usuario_inexistente(self):
        result = ReportService.reporte_por_usuario(999)
        self.assertIsNone(result["usuario"])
        self.assertEqual(result["viajes"], [])
        self.assertEqual(result["total_viajes"], 0)
        self.assertEqual(result["total_gasto"], 0)
        self.assertEqual(result["promedio_duracion"], 0)

    def test_generar_csv_viajes(self):
        rentals = self.crear_rentals_finalizados()
        csv_content = ReportService.generar_csv_viajes(rentals)

        self.assertIn("ID,Usuario,Origen,Destino,Inicio,Fin,Duración (min),Costo,Estado", csv_content)
        self.assertIn("finalizado", csv_content)
        self.assertTrue("100.50" in csv_content or "50.00" in csv_content)
        self.assertGreaterEqual(csv_content.count("\n"), 2)

    def test_generar_pdf_general(self):
        resumen = {
            "total_viajes": 10,
            "total_usuarios": 5,
            "total_recaudado": Decimal("1000.00"),
            "promedio_duracion": 25.3,
            "co2_ev": 3.0,
        }
        buffer = ReportService.generar_pdf_general(resumen)
        data = buffer.getvalue()

        self.assertIsInstance(buffer, io.BytesIO)
        self.assertGreater(len(data), 1000)
        self.assertTrue(data.startswith(b"%PDF"))

    def test_generar_pdf_usuario_sin_viajes(self):
        data = {
            "usuario": self.usuario,
            "viajes": [],
            "total_viajes": 0,
            "total_gasto": Decimal("0.00"),
            "promedio_duracion": 0,
        }
        buffer = ReportService.generar_pdf_usuario(self.usuario, data)
        pdf_bytes = buffer.getvalue()

        self.assertIsInstance(buffer, io.BytesIO)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_generar_pdf_usuario_con_viajes(self):
        rentals = self.crear_rentals_finalizados()
        data = {
            "usuario": self.usuario,
            "viajes": rentals,
            "total_viajes": 2,
            "total_gasto": Decimal("150.50"),
            "promedio_duracion": 30.0,
        }
        buffer = ReportService.generar_pdf_usuario(self.usuario, data)
        pdf_bytes = buffer.getvalue()

        self.assertIsInstance(buffer, io.BytesIO)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
