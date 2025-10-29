import stripe
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from stripe import CardError, InvalidRequestError, APIConnectionError

from apps.payment.models import MetodoTarjeta
from apps.wallet.models import Wallet
from apps.transactions.services.transaction_service import TransactionService

# Configura la clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class RecargarSaldoService:
    """
    Servicio encargado de crear el PaymentIntent en Stripe
    cuando el usuario realiza una recarga de saldo en su wallet.
    Integra la actualización local inmediata del balance.
    """

    def __init__(self, usuario, amount, payment_method_id=None):
        self.usuario = usuario
        self.amount = Decimal(str(amount))
        self.amount_cents = int(self.amount * 100)  # Stripe trabaja en centavos
        self.currency = "cop"
        self.payment_method_id = payment_method_id  # ✅ Tarjeta seleccionada por el usuario

    def obtener_metodo_pago(self):
        """
        Devuelve el método de pago correcto:
        - Si el usuario especifica un payment_method_id, lo usa.
        - Si no, toma la primera tarjeta registrada.
        """
        if self.payment_method_id:
            metodo = MetodoTarjeta.objects.filter(
                usuario=self.usuario,
                stripe_payment_method_id=self.payment_method_id
            ).first()
        else:
            metodo = MetodoTarjeta.objects.filter(usuario=self.usuario).first()

        if not metodo:
            raise Exception("No se encontró una tarjeta válida para este usuario.")
        if not metodo.stripe_customer_id:
            raise Exception("El método de pago no tiene un cliente (customer_id) asociado.")
        return metodo

    @transaction.atomic
    def crear_payment_intent(self):
        """
        Crea un PaymentIntent en Stripe con el método y customer del usuario.
        Si el pago es exitoso, registra inmediatamente la transacción en la wallet local.
        """
        metodo = self.obtener_metodo_pago()

        try:
            user_pk = getattr(self.usuario, "usuario_id", self.usuario.pk)
            user_identifier = getattr(self.usuario, "email", str(self.usuario))

            intent = stripe.PaymentIntent.create(
                amount=self.amount_cents,
                currency=self.currency,
                customer=metodo.stripe_customer_id,   # ✅ Cliente asociado
                payment_method=metodo.stripe_payment_method_id,  # ✅ Tarjeta elegida
                confirm=True,
                off_session=True,
                description=f"Recarga de saldo – {user_identifier}",
                metadata={
                    "user_id": str(user_pk),
                    "email": getattr(self.usuario, "email", ""),
                    "nombre": getattr(self.usuario, "nombre", ""),
                    "apellido": getattr(self.usuario, "apellido", ""),
                    "origen": "wallet_recarga"
                },
            )

            # 🔹 Si el pago fue exitoso, reflejarlo de inmediato en la base local
            if intent.status == "succeeded":
                wallet, _ = Wallet.objects.get_or_create(usuario=self.usuario)
                TransactionService.registrar_movimiento(
                    wallet=wallet,
                    tipo="RECARGA",
                    monto=self.amount,
                    descripcion=f"Recarga vía Stripe ({intent.id})"
                )

            return {
                "intent_id": intent.id,
                "status": intent.status,
                "amount": float(self.amount),
                "currency": intent.currency.upper(),
                "stripe_created": intent.created,
            }

        except CardError as e:
            raise Exception(f"Error de tarjeta: {e.user_message}")
        except InvalidRequestError as e:
            raise Exception(f"Error de solicitud a Stripe: {e.user_message}")
        except APIConnectionError:
            raise Exception("Error de conexión con Stripe, inténtalo de nuevo.")
        except Exception as e:
            raise Exception(f"Error al crear el pago: {str(e)}")
