from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
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
        # ENCABEZADO CON LOGO Y TÍTULO
        # ============================
        header_data = []
        
        try:
            # Intenta cargar el logo (ajusta la ruta según tu proyecto)
            logo_path = "static/users/images/logo.png"
            logo = Image(logo_path, width=1.2 * inch, height=1.2 * inch)
            header_data.append([logo, ""])
        except Exception:
            # Si no hay logo, espacio vacío
            header_data.append(["", ""])

        header_table = Table(header_data, colWidths=[2 * inch, 4.5 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 10))

        # Título principal
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#38a169"),
            spaceAfter=6,
            alignment=0,
            fontName="Helvetica-Bold"
        )
        elements.append(Paragraph("FACTURA DE VIAJE", title_style))

        # Subtítulo
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#718096"),
            spaceAfter=20,
        )
        elements.append(Paragraph("Sistema de Movilidad Urbana TwoMove", subtitle_style))
        
        # Línea separadora verde
        elements.append(Spacer(1, 5))
        line_table = Table([["", ""]], colWidths=[6.6 * inch, 0.1 * inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 3, colors.HexColor("#38a169")),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 15))

        # ============================
        # INFORMACIÓN DE FACTURA Y CLIENTE
        # ============================
        info_header_style = ParagraphStyle(
            "InfoHeader",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#2d3748"),
            fontName="Helvetica-Bold",
            spaceAfter=8,
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f7fafc")),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#2d3748")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        # ============================
        # DETALLES DEL VIAJE
        # ============================
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#2d3748"),
            spaceAfter=10,
            fontName="Helvetica-Bold"
        )
        elements.append(Paragraph("DETALLES DEL VIAJE", section_style))

        # Formatear fechas
        hora_inicio = rental.hora_inicio.strftime('%d/%m/%Y %I:%M %p') if rental.hora_inicio else "N/A"
        hora_fin = rental.hora_fin.strftime('%d/%m/%Y %I:%M %p') if rental.hora_fin else "N/A"

        detail_data = [
            [
                Paragraph("<b>Concepto</b>", styles["Normal"]),
                Paragraph("<b>Detalle</b>", styles["Normal"])
            ],
            [
                Paragraph("🕐 Hora de inicio", styles["Normal"]),
                Paragraph(hora_inicio, styles["Normal"])
            ],
            [
                Paragraph("🏁 Hora de finalización", styles["Normal"]),
                Paragraph(hora_fin, styles["Normal"])
            ],
            [
                Paragraph("⏱️ Duración total", styles["Normal"]),
                Paragraph(f"<b>{duracion_minutos:.1f} minutos</b>", styles["Normal"])
            ],
            [
                Paragraph("📍 Estación de origen", styles["Normal"]),
                Paragraph(rental.estacion_origen.nombre if rental.estacion_origen else "N/A", styles["Normal"])
            ],
            [
                Paragraph("🎯 Estación de destino", styles["Normal"]),
                Paragraph(
                    rental.estacion_destino.nombre if rental.estacion_destino else "🚨 Fuera de estación",
                    styles["Normal"]
                )
            ],
            [
                Paragraph("🚲 Bicicleta asignada", styles["Normal"]),
                Paragraph(rental.bike.numero_serie if rental.bike else "N/A", styles["Normal"])
            ],
            [
                Paragraph("💳 Método de pago", styles["Normal"]),
                Paragraph(rental.metodo_pago.replace('_', ' ').title(), styles["Normal"])
            ],
        ]

        detail_table = Table(detail_data, colWidths=[2.2 * inch, 4.4 * inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#48bb78")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(detail_table)
        elements.append(Spacer(1, 25))

        # ============================
        # RESUMEN DE COBRO
        # ============================
        elements.append(Paragraph("RESUMEN DE COBRO", section_style))

        costo_formateado = f"${costo_total:,.0f} COP"
        
        total_data = [
            [
                Paragraph("<b>Concepto</b>", styles["Normal"]),
                Paragraph("<b>Monto</b>", styles["Normal"])
            ],
            [
                Paragraph("Costo del servicio", styles["Normal"]),
                Paragraph(costo_formateado, styles["Normal"])
            ],
            [
                Paragraph("IVA (0%)", styles["Normal"]),
                Paragraph("$0 COP", styles["Normal"])
            ],
            [
                Paragraph("Descuentos", styles["Normal"]),
                Paragraph("$0 COP", styles["Normal"])
            ],
            [
                "",
                ""
            ],
            [
                Paragraph("<b>TOTAL A PAGAR</b>", 
                    ParagraphStyle("TotalLabel", parent=styles["Normal"], fontSize=12, fontName="Helvetica-Bold")),
                Paragraph(f"<b>{costo_formateado}</b>",
                    ParagraphStyle("TotalAmount", parent=styles["Normal"], fontSize=14, fontName="Helvetica-Bold", 
                                 textColor=colors.HexColor("#38a169")))
            ],
        ]

        total_table = Table(total_data, colWidths=[4.6 * inch, 2 * inch])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#48bb78")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor("#f0fff4")),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 4), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, 4), [colors.white, colors.HexColor("#f7fafc")]),
            ('GRID', (0, 0), (-1, 4), 0.5, colors.HexColor("#e2e8f0")),
            ('BOX', (0, 5), (-1, 5), 2, colors.HexColor("#38a169")),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 30))

        # ============================
        # INFORMACIÓN ADICIONAL
        # ============================
        info_box_style = ParagraphStyle(
            "InfoBox",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#4a5568"),
            leading=12,
            spaceAfter=5,
        )
        
        info_adicional = [
            ["<b>📋 INFORMACIÓN IMPORTANTE</b>"],
            ["• Esta factura es un comprobante de pago digital generado automáticamente."],
            ["• El cobro se realizó mediante el método de pago registrado en su cuenta."],
            ["• Para consultas o reclamos, contáctenos a soporte@twomove.co"],
            ["• Este documento no requiere firma ni sello para su validez."],
        ]
        
        for line in info_adicional:
            elements.append(Paragraph(line[0], info_box_style))
        
        elements.append(Spacer(1, 20))

        # ============================
        # PIE DE PÁGINA
        # ============================
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#718096"),
            alignment=1,
            leading=12,
        )
        footer_text = (
            "<b>Gracias por viajar con TwoMove 🚴‍♂️</b><br/>"
            "Sistema de Movilidad Urbana Inteligente<br/>"
            "www.twomove.co | soporte@twomove.co<br/>"
            f"© {datetime.now().year} TwoMove SAS - Todos los derechos reservados"
        )
        elements.append(Paragraph(footer_text, footer_style))

        # Generar PDF con canvas personalizado
        doc.build(elements, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer