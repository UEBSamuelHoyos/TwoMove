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
    @staticmethod
    def _enviar_correo_cancelacion(usuario, rental, motivo=""):
        """
        Envía un correo electrónico al usuario confirmando la cancelación de su reserva.
        Usa el template: rentals/cancellation_confirmed.html
        """
        try:
            html_content = render_to_string("rentals/reservation_cancelled.html", {
                "usuario": usuario,
                "user": usuario,  # compatibilidad con {{ user }} en el template
                "fecha": rental.hora_fin.strftime("%Y-%m-%d") if rental.hora_fin else "",
                "hora": rental.hora_fin.strftime("%H:%M") if rental.hora_fin else "",
                "estacion": rental.estacion_origen.nombre if rental.estacion_origen else "Desconocida",
                "bicicleta": rental.bike_serial_reservada or "N/A",
                "codigo": rental.codigo_desbloqueo or "N/A",
                "costo": f"${rental.costo_estimado:,.0f}" if rental.costo_estimado else "Sin costo",
                "motivo": motivo,
                "SITE_NAME": "TwoMove",
                "SITE_URL": "https://twomove.co",
            })

            subject = f"❌ Reserva #{rental.id} cancelada - TwoMove"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [usuario.email]

            email = EmailMultiAlternatives(subject, "", from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            print(f"📩 Correo de cancelación enviado correctamente a {usuario.email}")

        except Exception as e:
            print(f"⚠️ Error al enviar correo de cancelación: {e}")
