from django.utils import timezone
from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from apps.rentals.models import Rental
from apps.bikes.models import Bike
from apps.stations.models import Station
from apps.transactions.models import WalletTransaccion
from apps.wallet.models import Wallet

# ✅ Patrón Decorator para cálculo de costos
from apps.rentals.services.cost_decorator import (
    CostoBase,
    CostoPorTiempoExtra,
    CostoPorFueraDeEstacion,
)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io


class TripEndService:
    """
    Servicio encargado de finalizar un viaje activo y generar la factura.
    """

    @staticmethod
    @transaction.atomic
    def end_trip(usuario, rental_id: int, estacion_destino_id: int = None):
        user_pk = getattr(usuario, "pk", None)
        print(f"🧩 Finalizando viaje rental_id={rental_id} usuario_pk={user_pk}")

        try:
            rental = Rental.objects.select_related("bike", "usuario", "estacion_origen").get(
                pk=rental_id, usuario=usuario
            )
        except Rental.DoesNotExist:
            raise ValueError("No se encontró el viaje activo para este usuario.")
        except Exception as e:
            print(f"⚠️ Error cargando Rental: {e}")
            raise

        try:
            # ------------------------------------------------------------------
            # Validaciones iniciales
            # ------------------------------------------------------------------
            if rental.estado != "activo":
                raise ValueError(f"El viaje no está activo (estado actual: {rental.estado}).")

            bike = rental.bike

            # ✅ Si no se envía estación destino, se usa la definida al reservar
            estacion_destino = None
            if estacion_destino_id:
                estacion_destino = Station.objects.filter(pk=estacion_destino_id).first()
                if not estacion_destino:
                    raise ValueError("Estación destino no encontrada.")
            elif rental.estacion_destino:
                estacion_destino = rental.estacion_destino

            # ------------------------------------------------------------------
            # Cálculo de duración y costos
            # ------------------------------------------------------------------
            hora_fin = timezone.now()
            duracion = (hora_fin - rental.hora_inicio).total_seconds() / 60
            duracion_min = float(f"{duracion:.1f}")

            print(f"🕒 Duración calculada: {duracion_min} min")

            fuera_estacion = estacion_destino is None

            componente = CostoBase()
            componente = CostoPorTiempoExtra(componente)
            componente = CostoPorFueraDeEstacion(componente)

            costo_total = componente.calcular(
                rental=rental,
                duracion_min=duracion_min,
                fuera_estacion=fuera_estacion,
            )
            print(f"💰 Costo total calculado: {costo_total}")

            # ------------------------------------------------------------------
            # Actualizar Rental y Bicicleta
            # ------------------------------------------------------------------
            rental.estado = "finalizado"
            rental.hora_fin = hora_fin
            rental.estacion_destino = estacion_destino
            rental.costo_total = Decimal(costo_total)
            rental.save(update_fields=["estado", "hora_fin", "estacion_destino", "costo_total"])

            bike.estado = "block"
            bike.station = estacion_destino if estacion_destino else bike.station
            bike.save(update_fields=["estado", "station"])

            # ------------------------------------------------------------------
            # Registrar transacción Wallet
            # ------------------------------------------------------------------
            wallet = Wallet.objects.filter(usuario=usuario).first()
            if wallet:
                nuevo_saldo = wallet.balance - Decimal(costo_total)

                WalletTransaccion.objects.create(
                    wallet=wallet,
                    tipo="PAGO",  # ✅ tipo válido según tu modelo
                    monto=-Decimal(costo_total),
                    descripcion=f"Pago por finalización de viaje #{rental.id}",
                    saldo_resultante=nuevo_saldo,
                    referencia_externa=f"rental_{rental.id}"
                )

                wallet.balance = nuevo_saldo
                wallet.save(update_fields=["balance"])
                print(f"💳 Transacción registrada en wallet. Nuevo saldo: {wallet.balance}")

            # ------------------------------------------------------------------
            # Generar y enviar factura
            # ------------------------------------------------------------------
            print("📄 Generando factura PDF…")
            factura_pdf = TripEndService._generar_factura_pdf(rental, costo_total, duracion_min)

            print("📧 Enviando correo…")
            TripEndService._enviar_correo_factura(usuario, rental, costo_total, duracion_min, factura_pdf, fuera_estacion)

            print(f"✅ Viaje finalizado correctamente — Rental #{rental.id}")

            return {
                "mensaje": "✅ Viaje finalizado correctamente",
                "costo_total": round(float(costo_total), 2),
                "duracion_minutos": round(duracion_min, 1),
                "estado_bicicleta": bike.estado,
                "estacion_destino": getattr(estacion_destino, "nombre", "N/A"),
            }

        except Exception as e:
            print(f"❌ Error general en TripEndService.end_trip: {e}")
            raise

    # ------------------------------------------------------------------
    # 📄 Generación de factura PDF
    # ------------------------------------------------------------------
    @staticmethod
    def _generar_factura_pdf(rental, costo_total, duracion):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 12)

        p.drawString(100, 750, "Factura del Servicio TwoMove")
        p.drawString(100, 730, f"Usuario: {rental.usuario.email}")
        p.drawString(100, 710, f"Bicicleta: {getattr(rental, 'bike_serial_reservada', None) or rental.bike.numero_serie}")
        p.drawString(100, 690, f"Duración: {duracion:.1f} minutos")
        p.drawString(100, 670, f"Costo total: ${Decimal(costo_total):.2f}")
        p.drawString(100, 650, f"Estación destino: {rental.estacion_destino.nombre if rental.estacion_destino else 'N/A'}")
        p.drawString(100, 630, f"Fecha: {rental.hora_fin.strftime('%Y-%m-%d %H:%M:%S')}")

        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    # ------------------------------------------------------------------
    # 📧 Envío de correo con factura PDF adjunta
    # ------------------------------------------------------------------
    @staticmethod
    def _enviar_correo_factura(usuario, rental, costo_total, duracion, pdf_buffer, fuera_estacion):
        try:
            # ✅ Contexto completo para el template
            context = {
                "usuario": usuario,
                "rental": rental,
                "costo_total": f"${round(float(costo_total), 2):,.0f}",  # Formato: $17,500
                "duracion": round(duracion, 1),
                "fecha_fin": rental.hora_fin.strftime('%d de %B de %Y, %I:%M %p'),
                "fuera_estacion": fuera_estacion,
                "now": timezone.now(),
            }

            html_content = render_to_string("rentals/trip_finished.html", context)
            subject = f"🚴 Tu viaje ha finalizado – Factura #{rental.id}"
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            to_email = [usuario.email]

            msg = EmailMultiAlternatives(subject, "", from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.attach(
                f"Factura_TwoMove_{rental.id}.pdf",
                pdf_buffer.getvalue(),
                "application/pdf"
            )
            msg.send(fail_silently=False)

            print(f"📩 Correo con factura enviado a {usuario.email}")

        except Exception as e:
            print(f"⚠️ Error al enviar correo de factura: {e}")