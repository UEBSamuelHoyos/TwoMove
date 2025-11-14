from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.pdfgen import canvas
from datetime import datetime


class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado para agregar número de página y líneas decorativas"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawRightString(
            7.5 * inch, 0.5 * inch,
            f"Página {self._pageNumber} de {page_count}"
        )


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
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=60
        )

        styles = getSampleStyleSheet()
        elements = []

        # ============================
        # ENCABEZADO CORPORATIVO
        # ============================
        header_table_data = []

        try:
            logo_path = "static/users/images/logo.png"
            logo = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
        except:
            logo = ""

        company_info = Paragraph(
            """
            <para align="right">
            <b><font size=14 color="#2D3748">TwoMove SAS</font></b><br/>
            <font size=10 color="#4A5568">Sistema de Movilidad Urbana Inteligente</font><br/>
            <font size=9 color="#4A5568">www.twomove.co<br/>soporte@twomove.co</font>
            </para>
            """,
            styles["Normal"]
        )

        header_table_data.append([logo, company_info])

        header_table = Table(header_table_data, colWidths=[2 * inch, 4.8 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#CBD5E0"))
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))

        # Título
        elements.append(Paragraph(
            "<b><font size=22 color='#2D3748'>FACTURA DE VIAJE</font></b>",
            styles["Title"]
        ))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph(
            "<font size=11 color='#718096'>Comprobante de servicio - TwoMove</font>",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 20))

        # ============================
        # INFORMACIÓN DE FACTURA & CLIENTE
        # ============================
        info_header_style = ParagraphStyle(
            "InfoHeader",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#2D3748"),
            fontName="Helvetica-Bold",
            spaceAfter=6,
        )

        fecha_actual = datetime.now().strftime('%d de %B de %Y, %I:%M %p')

        info_data = [
            [
                Paragraph("<b>INFORMACIÓN DE FACTURA</b>", info_header_style),
                Paragraph("<b>INFORMACIÓN DEL CLIENTE</b>", info_header_style)
            ],
            [
                Paragraph(f"<b>Nº de Factura:</b> INV-{rental.id:06d}", styles["Normal"]),
                Paragraph(f"<b>Cliente:</b> {rental.usuario.email}", styles["Normal"])
            ],
            [
                Paragraph(f"<b>Fecha de emisión:</b><br/>{fecha_actual}", styles["Normal"]),
                Paragraph(f"<b>ID de Usuario:</b> {rental.usuario.id}", styles["Normal"])
            ],
            [
                Paragraph(f"<b>ID de Viaje:</b> #{rental.id}", styles["Normal"]),
                Paragraph(f"<b>Tipo de viaje:</b> {rental.tipo_viaje.replace('_', ' ').title()}", styles["Normal"])
            ],
        ]

        info_table = Table(info_data, colWidths=[3.3 * inch, 3.3 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#2D3748")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#CBD5E0")),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 25))

        # ============================
        # DETALLES DEL VIAJE
        # ============================
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#2D3748"),
            spaceAfter=12,
            fontName="Helvetica-Bold"
        )
        elements.append(Paragraph("DETALLES DEL VIAJE", section_style))

        hora_inicio = rental.hora_inicio.strftime('%d/%m/%Y %I:%M %p') if rental.hora_inicio else "N/A"
        hora_fin = rental.hora_fin.strftime('%d/%m/%Y %I:%M %p') if rental.hora_fin else "N/A"

        detail_data = [
            ["<b>Concepto</b>", "<b>Detalle</b>"],
            ["🕐 Hora de inicio", hora_inicio],
            ["🏁 Hora de finalización", hora_fin],
            ["⏱️ Duración total", f"{duracion_minutos:.1f} minutos"],
            ["📍 Estación de origen", rental.estacion_origen.nombre if rental.estacion_origen else "N/A"],
            ["🎯 Estación de destino",
                rental.estacion_destino.nombre if rental.estacion_destino else "🚨 Fuera de estación"],
            ["🚲 Bicicleta asignada", rental.bike.numero_serie if rental.bike else "N/A"],
            ["💳 Método de pago", rental.metodo_pago.replace('_', ' ').title()],
        ]

        detail_table = Table(detail_data, colWidths=[2.2 * inch, 4.4 * inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#38A169")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
                colors.white, colors.HexColor("#F7FAFC")
            ]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ]))
        elements.append(detail_table)
        elements.append(Spacer(1, 30))

        # ============================
        # RESUMEN DE COBRO
        # ============================
        elements.append(Paragraph("RESUMEN DE COBRO", section_style))

        costo_formateado = f"${costo_total:,.0f} COP"

        total_data = [
            ["<b>Concepto</b>", "<b>Monto</b>"],
            ["Costo del servicio", costo_formateado],
            ["IVA (0%)", "$0 COP"],
            ["Descuentos", "$0 COP"],
            ["", ""],
            ["<b>TOTAL A PAGAR</b>", f"<b><font color='#38A169'>{costo_formateado}</font></b>"],
        ]

        total_table = Table(total_data, colWidths=[4.6 * inch, 2 * inch])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#38A169")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor("#F0FFF4")),
            ('BOX', (0, 5), (-1, 5), 2, colors.HexColor("#38A169")),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 5), (-1, 5), 14),
            ('GRID', (0, 0), (-1, 4), 0.5, colors.HexColor("#CBD5E0")),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 35))

        # ============================
        # INFORMACIÓN ADICIONAL
        # ============================
        info_box_style = ParagraphStyle(
            "InfoBox",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#4A5568"),
            leading=13,
            spaceAfter=4,
        )

        info_text = [
            "<b>📋 INFORMACIÓN IMPORTANTE</b>",
            "• Esta factura es un comprobante de pago digital generado automáticamente.",
            "• El cobro se realizó mediante el método de pago registrado en su cuenta.",
            "• Para consultas o reclamos, contáctenos a soporte@twomove.co",
            "• Este documento no requiere firma ni sello para su validez.",
        ]

        for line in info_text:
            elements.append(Paragraph(line, info_box_style))

        elements.append(Spacer(1, 30))

        # ============================
        # PIE DE PÁGINA PREMIUM
        # ============================
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#718096"),
            alignment=1,
            leading=13,
        )

        footer_text = f"""
        <para align="center">
        <font size=11 color="#2D3748"><b>Gracias por viajar con TwoMove</b></font><br/>
        <font size=9 color="#718096">
        Sistema de Movilidad Urbana Inteligente<br/>
        www.twomove.co | soporte@twomove.co<br/>
        © {datetime.now().year} TwoMove SAS – Todos los derechos reservados
        </font>
        </para>
        """

        elements.append(Paragraph(footer_text, footer_style))

        # GENERAR PDF
        doc.build(elements, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer
