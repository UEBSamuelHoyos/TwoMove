# apps/admin_dashboard/services/report_service.py
import csv
import io
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from django.db.models import Sum
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from apps.rentals.models import Rental
from apps.users.models import Usuario


class ReportService:
    """
    Servicio para generar reportes generales o por usuario.
    """

    # ============================================================
    # 📊 Reporte general
    # ============================================================
    @staticmethod
    def resumen_general():
        """Devuelve datos agregados de toda la operación."""
        rentals = Rental.objects.filter(estado="finalizado")

        total_viajes = rentals.count()
        total_usuarios = rentals.values("usuario").distinct().count()
        total_recaudado = rentals.aggregate(total=Sum("costo_total"))["total"] or Decimal("0.00")

        # Duración promedio
        duraciones = [
            (r.hora_fin - r.hora_inicio).total_seconds() / 60
            for r in rentals if r.hora_inicio and r.hora_fin
        ]
        promedio_duracion = round(sum(duraciones) / len(duraciones), 1) if duraciones else 0

        # Estimación de CO₂ evitado: 0.3 kg por viaje
        co2_ev = round(total_viajes * 0.3, 2)

        return {
            "total_viajes": total_viajes,
            "total_usuarios": total_usuarios,
            "total_recaudado": total_recaudado,
            "promedio_duracion": promedio_duracion,
            "co2_ev": co2_ev,
        }

    # ============================================================
    # 👤 Reporte por usuario
    # ============================================================
    @staticmethod
    def reporte_por_usuario(usuario_id: int):
        """
        Devuelve los viajes y métricas de un usuario.
        Incluye validaciones de existencia y registros vacíos.
        """
        try:
            usuario = Usuario.objects.get(usuario_id=usuario_id)
        except Usuario.DoesNotExist:
            print(f"❌ Usuario con ID {usuario_id} no existe.")
            return {
                "viajes": [],
                "total_viajes": 0,
                "total_gasto": 0,
                "promedio_duracion": 0,
                "usuario": None,
            }

        viajes = (
            Rental.objects.filter(usuario_id=usuario_id)
            .select_related("estacion_origen", "estacion_destino")
            .order_by("-hora_inicio")
        )

        total_viajes = viajes.count()
        total_gasto = viajes.aggregate(total=Sum("costo_total"))["total"] or Decimal("0.00")

        duraciones = [
            (r.hora_fin - r.hora_inicio).total_seconds() / 60
            for r in viajes if r.hora_inicio and r.hora_fin
        ]
        promedio_duracion = round(sum(duraciones) / len(duraciones), 1) if duraciones else 0

        print(f"✅ Usuario {usuario.email} - viajes: {total_viajes}, gasto: {total_gasto}, promedio: {promedio_duracion}")

        return {
            "usuario": usuario,
            "viajes": viajes,
            "total_viajes": total_viajes,
            "total_gasto": total_gasto,
            "promedio_duracion": promedio_duracion,
        }

    # ============================================================
    # 🧾 Exportación CSV
    # ============================================================
    @staticmethod
    def generar_csv_viajes(viajes):
        """Crea un CSV a partir de una queryset de viajes."""
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "ID", "Usuario", "Origen", "Destino",
            "Inicio", "Fin", "Duración (min)", "Costo", "Estado"
        ])

        for r in viajes:
            duracion = (
                (r.hora_fin - r.hora_inicio).total_seconds() / 60
                if r.hora_inicio and r.hora_fin else ""
            )
            writer.writerow([
                r.id,
                getattr(r.usuario, "email", ""),
                getattr(r.estacion_origen, "nombre", ""),
                getattr(r.estacion_destino, "nombre", ""),
                r.hora_inicio.strftime("%Y-%m-%d %H:%M:%S") if r.hora_inicio else "",
                r.hora_fin.strftime("%Y-%m-%d %H:%M:%S") if r.hora_fin else "",
                f"{duracion:.1f}" if duracion else "",
                f"{r.costo_total:.2f}" if r.costo_total else "0",
                r.estado,
            ])

        buffer.seek(0)
        return buffer.getvalue()

    # ============================================================
    # 📄 PDF general
    # ============================================================
    @staticmethod
    def generar_pdf_general(resumen):
        """Genera un PDF con resumen general."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, 10.5 * inch, "Reporte General - TwoMove")

        c.setFont("Helvetica", 11)
        y = 10.1 * inch
        c.drawString(1 * inch, y, f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
        y -= 0.4 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y, "📊 Indicadores Generales")
        y -= 0.3 * inch
        c.setFont("Helvetica", 11)
        c.drawString(1 * inch, y, f"Total de viajes realizados: {resumen['total_viajes']}")
        y -= 0.25 * inch
        c.drawString(1 * inch, y, f"Usuarios activos: {resumen['total_usuarios']}")
        y -= 0.25 * inch
        c.drawString(1 * inch, y, f"Recaudo total: ${resumen['total_recaudado']:,.0f}")
        y -= 0.25 * inch
        c.drawString(1 * inch, y, f"CO₂ evitado (estimado): {resumen['co2_ev']} kg")
        y -= 0.25 * inch
        c.drawString(1 * inch, y, f"Duración promedio de viaje: {resumen['promedio_duracion']:.1f} min")

        # Línea divisoria
        c.setStrokeColor(colors.lightgrey)
        c.line(1 * inch, y - 0.15 * inch, 7.5 * inch, y - 0.15 * inch)

        # Firma institucional
        y -= 0.6 * inch
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.gray)
        c.drawString(1 * inch, y, "TwoMove – Sistema de Movilidad Sostenible")
        c.drawString(1 * inch, y - 0.2 * inch, "Documento generado automáticamente por el panel administrativo.")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    # ============================================================
    # 📄 PDF individual por usuario
    # ============================================================
    @staticmethod
    def generar_pdf_usuario(usuario, data):
        """Genera un PDF con los viajes y totales de un usuario."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, 10.5 * inch, "Reporte Individual de Usuario - TwoMove")

        c.setFont("Helvetica", 11)
        y = 10.1 * inch
        c.drawString(1 * inch, y, f"Usuario: {usuario.email}")
        y -= 0.25 * inch
        c.drawString(1 * inch, y, f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
        y -= 0.4 * inch

        # Resumen
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y, "📊 Resumen del Usuario")
        y -= 0.3 * inch
        c.setFont("Helvetica", 11)
        c.drawString(1 * inch, y, f"Total de viajes realizados: {data['total_viajes']}")
        y -= 0.25 * inch
        c.drawString(1 * inch, y, f"Duración promedio: {data['promedio_duracion']:.1f} min")
        y -= 0.25 * inch
        c.drawString(1 * inch, y, f"Gasto total acumulado: ${data['total_gasto']:,.0f}")

        y -= 0.3 * inch
        c.setStrokeColor(colors.lightgrey)
        c.line(1 * inch, y, 7.5 * inch, y)
        y -= 0.3 * inch

        # Tabla
        if not data["viajes"]:
            c.setFont("Helvetica-Oblique", 10)
            c.setFillColor(colors.gray)
            c.drawString(1 * inch, y, "⚠️ No se encontraron viajes registrados para este usuario.")
        else:
            c.setFont("Helvetica-Bold", 10)
            columnas = ["Origen", "Destino", "Inicio", "Duración", "Costo"]
            x = [1 * inch, 2.6 * inch, 4.2 * inch, 5.6 * inch, 6.6 * inch]
            for i, col in enumerate(columnas):
                c.drawString(x[i], y, col)
            y -= 0.2 * inch
            c.line(1 * inch, y, 7.5 * inch, y)

            c.setFont("Helvetica", 9)
            y -= 0.25 * inch
            for r in data["viajes"][:25]:
                if y < 1 * inch:
                    c.showPage()
                    y = 10.5 * inch
                duracion = (
                    (r.hora_fin - r.hora_inicio).total_seconds() / 60
                    if r.hora_inicio and r.hora_fin else 0
                )
                c.drawString(1 * inch, y, getattr(r.estacion_origen, "nombre", "")[:14])
                c.drawString(2.6 * inch, y, getattr(r.estacion_destino, "nombre", "")[:14])
                c.drawString(4.2 * inch, y, r.hora_inicio.strftime("%d/%m/%y %H:%M") if r.hora_inicio else "-")
                c.drawString(5.6 * inch, y, f"{duracion:.1f} min")
                c.drawRightString(7.4 * inch, y, f"${r.costo_total or 0:,.0f}")
                y -= 0.22 * inch

        # Pie institucional
        y -= 0.3 * inch
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.gray)
        c.drawString(1 * inch, y, "TwoMove – Sistema de Movilidad Sostenible")
        c.drawString(1 * inch, y - 0.15 * inch, "Documento generado automáticamente por el panel administrativo.")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
