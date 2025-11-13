from django.db import transaction
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from apps.rentals.models import Rental
from apps.wallet.models import Wallet
from apps.transactions.services.transaction_service import TransactionService


class CancellationService:
    """
    Servicio encargado de manejar las cancelaciones de reservas.

    - Verifica que la reserva pertenezca al usuario autenticado.
    - Permite cancelar solo si la reserva está en estado 'reservado'.
    - Procesa reembolsos si el pago fue con wallet o stripe.
    - Envía notificación por correo electrónico.
    """

    @staticmethod
    @transaction.atomic
    def cancel_reservation(user, rental_id: int, reason: str = ""):
        """
        Cancela una reserva y procesa el reembolso según el método de pago.

        :param user: instancia del usuario autenticado
        :param rental_id: ID de la reserva a cancelar
        :param reason: texto opcional con el motivo de cancelación
        :return: dict con información de la cancelación
        """
        try:
            rental = Rental.objects.select_related("usuario", "bike", "estacion_origen").get(
                pk=rental_id, usuario=user
            )
        except Rental.DoesNotExist:
            raise ValueError("No se encontró la reserva o no pertenece a este usuario.")

        # Validar estado
        estado_actual = (rental.estado or "").lower()
        if estado_actual not in ["reservado"]:
            raise ValueError("Esta reserva no puede ser cancelada porque ya fue iniciada o finalizada.")

        # Actualizar estado y registrar cancelación
        rental.estado = "cancelado"
        rental.hora_fin = timezone.now()
        rental.actualizado_en = timezone.now()
        rental.save(update_fields=["estado", "hora_fin", "actualizado_en"])

        # Procesar reembolso si aplica
        refund_amount = Decimal(rental.costo_estimado or 0)

        if refund_amount > 0:
            if rental.metodo_pago == "wallet":
                wallet = Wallet.objects.select_for_update().get(usuario=user)
                TransactionService.registrar_movimiento(
                    wallet=wallet,
                    tipo="REEMBOLSO",
                    monto=refund_amount,
                    descripcion=f"Reembolso por cancelación de reserva #{rental.id}"
                )
            elif rental.metodo_pago == "stripe":
                # Aquí podrías implementar refund real si tienes payment_intent_id
                pass

        # 📩 Enviar correo de notificación
        CancellationService._enviar_correo_cancelacion(user, rental, reason)

        print(f"❌ Reserva #{rental.id} cancelada correctamente por {user.email}")

        return {
            "status": "cancelled",
            "rental_id": rental.id,
            "estado": rental.estado,
            "payment_method": rental.metodo_pago,
            "refunded_amount": float(refund_amount) if refund_amount > 0 else 0,
            "cancelled_at": rental.hora_fin.strftime("%Y-%m-%d %H:%M:%S"),
            "reason": reason or "Sin motivo especificado",
        }

    # -----------------------------------------------------------
    # 📧 Envío de correo de cancelación
    # -----------------------------------------------------------
# -----------------------------------------------------------
    # 📧 Envío de correo de cancelación
    # -----------------------------------------------------------
    @staticmethod
    def _enviar_correo_cancelacion(usuario, rental, motivo=""):
        """
        Envía un correo electrónico al usuario confirmando la cancelación de su reserva.
        Usa el template: rentals/reservation_cancelled.html
        """
        try:
            # Calcular el reembolso
            refund_amount = Decimal(rental.costo_estimado or 0)
            reembolso_texto = f"${refund_amount:,.0f} COP" if refund_amount > 0 else "Sin costo"
            
            # Contexto para el template
            ctx = {
                "usuario": usuario,
                "rental": rental,
                "fecha": rental.hora_fin.strftime("%Y-%m-%d") if rental.hora_fin else timezone.now().strftime("%Y-%m-%d"),
                "hora": rental.hora_fin.strftime("%H:%M") if rental.hora_fin else timezone.now().strftime("%H:%M"),
                "estacion_origen": rental.estacion_origen.nombre if rental.estacion_origen else "Desconocida",
                "estacion_destino": rental.estacion_destino.nombre if rental.estacion_destino else "N/A",
                "bike_serial": rental.bike_serial_reservada or "No asignada",
                "codigo": rental.codigo_desbloqueo or "N/A",
                "reembolso": reembolso_texto,
                "motivo": motivo or "",
            }

            html_content = render_to_string("rentals/reservation_cancelled.html", ctx)

            # Texto plano de respaldo
            text_content = (
                f"Hola {getattr(usuario, 'nombre', usuario.email)}.\n\n"
                f"Tu reserva #{rental.id} ha sido cancelada exitosamente.\n"
                f"Origen: {ctx['estacion_origen']}\n"
                f"Destino: {ctx['estacion_destino']}\n"
                f"Bicicleta: {ctx['bike_serial']}\n"
                f"Reembolso: {ctx['reembolso']}\n"
                f"Motivo: {motivo or 'Sin motivo especificado'}\n\n"
                "Gracias por usar TwoMove."
            )

            subject = f"❌ Reserva #{rental.id} cancelada - TwoMove"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [usuario.email]

            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            print(f"📩 Correo de cancelación enviado correctamente a {usuario.email}")

        except Exception as e:
            print(f"⚠️ Error al enviar correo de cancelación: {e}")
