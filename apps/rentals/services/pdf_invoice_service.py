from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from datetime import datetime


class PDFInvoiceService:
    """
    Genera una factura PDF profesional con resumen del viaje TwoMove.
    """

    @staticmethod
    def generar_factura_pdf(rental, costo_total, duracion_minutos):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        elements = []

        # ============================
        # ENCABEZADO
        # ============================
        try:
            # Si tienes logo en static (ajusta la ruta)
            logo_path = "static/images/twomove_logo.png"
            elements.append(Image(logo_path, width=1.5 * inch, height=1.5 * inch))
        except Exception:
            pass

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=18,
            alignment=1,
            textColor=colors.HexColor("#0066cc"),
        )
        elements.append(Paragraph("Factura de Viaje", title_style))
        elements.append(Spacer(1, 12))

        sub_style = ParagraphStyle(
            "Sub",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.gray,
        )

        info_data = [
            [f"<b>ID de viaje:</b> {rental.id}", f"<b>Fecha:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
            [f"<b>Usuario:</b> {rental.usuario.email}", f"<b>Tipo de viaje:</b> {rental.tipo_viaje.capitalize()}"],
            [f"<b>Inicio:</b> {rental.hora_inicio.strftime('%Y-%m-%d %H:%M:%S')}", f"<b>Fin:</b> {rental.hora_fin.strftime('%Y-%m-%d %H:%M:%S')}"],
        ]

        info_table = Table(info_data, colWidths=[3.3 * inch, 3.3 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 18))

        # ============================
        # DETALLES DEL VIAJE
        # ============================
        detail_data = [
            ["Detalle", "Información"],
            ["Duración", f"{duracion_minutos:.1f} minutos"],
            ["Estación de origen", rental.estacion_origen.nombre if rental.estacion_origen else "N/A"],
            ["Estación de destino", rental.estacion_destino.nombre if rental.estacion_destino else "N/A"],
            ["Bicicleta", rental.bike.numero_serie if rental.bike else "N/A"],
            ["Método de pago", rental.metodo_pago.capitalize()],
        ]

        detail_table = Table(detail_data, colWidths=[2.5 * inch, 4.1 * inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0066cc")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        elements.append(detail_table)
        elements.append(Spacer(1, 18))

        # ============================
        # TOTALES
        # ============================
        total_data = [
            ["Subtotal", f"${costo_total:,.0f}"],
            ["IVA (0%)", "$0"],
            ["<b>Total a pagar</b>", f"<b>${costo_total:,.0f}</b>"]
        ]
        total_table = Table(total_data, colWidths=[4.5 * inch, 2 * inch])
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor("#009933")),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 20))

        # ============================
        # PIE DE PÁGINA
        # ============================
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.gray,
            alignment=1
        )
        footer_text = (
            "Gracias por viajar con <b>TwoMove</b> 🚴‍♂️<br/>"
            "Este documento es un comprobante de pago digital generado automáticamente.<br/>"
            "No requiere firma ni sello."
        )
        elements.append(Paragraph(footer_text, footer_style))

        # Generar PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
