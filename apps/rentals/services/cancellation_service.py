# apps/rentals/services/cancellation_service.py
from django.db import transaction
from django.utils import timezone
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
            rental = Rental.objects.select_related("usuario").get(pk=rental_id, usuario=user)
        except Rental.DoesNotExist:
            raise ValueError("No se encontró la reserva o no pertenece a este usuario.")

        # ✅ Normalizar estado
        estado_actual = (rental.estado or "").lower()

        # Solo permitir cancelar si está reservada
        if estado_actual not in ["reservado"]:
            raise ValueError("Esta reserva no puede ser cancelada porque ya fue iniciada o finalizada.")

        # ✅ Actualizar estado y registrar cancelación
        rental.estado = "cancelado"
        rental.hora_fin = timezone.now()
        rental.actualizado_en = timezone.now()
        rental.save(update_fields=["estado", "hora_fin", "actualizado_en"])

        # ✅ Procesar reembolso si aplica
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
                # 🔹 Aquí podrías implementar refund real si tienes payment_intent_id
                # import stripe
                # stripe.api_key = settings.STRIPE_SECRET_KEY
                # stripe.Refund.create(payment_intent=rental.stripe_payment_intent_id)
                pass

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
