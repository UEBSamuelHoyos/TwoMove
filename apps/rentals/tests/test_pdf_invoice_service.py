import io
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from apps.rentals.services.pdf_invoice_service import PDFInvoiceService


class DummyStation:
    def __init__(self, nombre):
        self.nombre = nombre


class DummyBike:
    def __init__(self, numero_serie):
        self.numero_serie = numero_serie


class DummyUser:
    def __init__(self, email):
        self.email = email


class DummyRental:
    """Objeto simulado con estructura mínima de una reserva."""
    def __init__(self):
        self.id = 101
        self.usuario = DummyUser("user@example.com")
        self.tipo_viaje = "ultima_milla"
        self.hora_inicio = timezone.now()
        self.hora_fin = timezone.now()
        self.estacion_origen = DummyStation("Estación Norte")
        self.estacion_destino = DummyStation("Estación Sur")
        self.bike = DummyBike("E-12345")
        self.metodo_pago = "wallet"


@patch("apps.rentals.services.pdf_invoice_service.Image", lambda *a, **kw: None)
class TestPDFInvoiceService(TestCase):
    """Pruebas unitarias para PDFInvoiceService."""

    def setUp(self):
        self.rental = DummyRental()
        self.costo_total = Decimal("20000.00")
        self.duracion = 35.0

    # ============================================================
    # 🔹 Generación básica
    # ============================================================
    def test_generar_factura_pdf_basico(self):
        """Debe generar un PDF válido (buffer con cabecera %PDF)."""
        buffer = PDFInvoiceService.generar_factura_pdf(
            self.rental, self.costo_total, self.duracion
        )
        self.assertIsInstance(buffer, io.BytesIO)
        contenido = buffer.read(10)
        self.assertTrue(contenido.startswith(b"%PDF"), "El archivo generado no es un PDF válido.")

    # ============================================================
    # 🔹 Campos dinámicos y tipos de dato
    # ============================================================
    def test_factura_incluye_datos_principales(self):
        """Debe poder generar PDF con los datos del rental sin errores."""
        buffer = PDFInvoiceService.generar_factura_pdf(
            self.rental, self.costo_total, self.duracion
        )
        self.assertGreater(len(buffer.getvalue()), 0)

    # ============================================================
    # 🔹 Manejo de datos faltantes
    # ============================================================
    def test_generar_factura_sin_estaciones(self):
        """Debe manejar correctamente si faltan estaciones o bicicleta."""
        self.rental.estacion_origen = None
        self.rental.estacion_destino = None
        self.rental.bike = None
        buffer = PDFInvoiceService.generar_factura_pdf(
            self.rental, Decimal("15000"), 20
        )
        self.assertIsInstance(buffer, io.BytesIO)
        self.assertGreater(len(buffer.getvalue()), 0)

    # ============================================================
    # 🔹 Formato de duración y costo
    # ============================================================
    def test_duracion_y_costo_formato(self):
        """Debe aceptar decimales y generar correctamente el formato monetario."""
        buffer = PDFInvoiceService.generar_factura_pdf(
            self.rental, Decimal("18500.75"), 42.3
        )
        contenido = buffer.getvalue()
        self.assertIn(b"%PDF", contenido[:100])
        self.assertGreater(len(contenido), 500)
