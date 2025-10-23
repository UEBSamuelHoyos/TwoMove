import stripe
from django.conf import settings
from payment.models import MetodoTarjeta
from stripe import CardError, InvalidRequestError, APIConnectionError  # Stripe v13 compatible

# Configura la clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class RecargarSaldoService:
    """
    Servicio encargado de crear el PaymentIntent en Stripe
    cuando el usuario realiza una recarga de saldo en su wallet.
    """

    def __init__(self, usuario, amount, payment_method_id=None):
        self.usuario = usuario
        self.amount = int(float(amount) * 100)  # Stripe trabaja en centavos
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

    def crear_payment_intent(self):
        """
        Crea un PaymentIntent en Stripe con el método y customer del usuario.
        """
        metodo = self.obtener_metodo_pago()

        try:
            user_pk = getattr(self.usuario, "usuario_id", self.usuario.pk)
            user_identifier = getattr(self.usuario, "email", str(self.usuario))

            intent = stripe.PaymentIntent.create(
                amount=self.amount,
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
                },
            )

            return {
                "intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,
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
