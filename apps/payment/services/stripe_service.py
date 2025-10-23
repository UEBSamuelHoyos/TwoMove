import stripe
from django.conf import settings
from apps.payment.models import MetodoTarjeta


stripe.api_key = settings.STRIPE_SECRET_KEY

def crear_setup_intent(usuario):
    # Buscar si ya tiene un customer_id
    metodo = MetodoTarjeta.objects.filter(usuario=usuario).first()

    if metodo and metodo.stripe_customer_id:
        customer_id = metodo.stripe_customer_id
    else:
        # Crear nuevo customer en Stripe
        customer = stripe.Customer.create(
            email=usuario.email,
            name=f"{usuario.nombre} {usuario.apellido}"
        )
        customer_id = customer.id

    return stripe.SetupIntent.create(
        customer=customer_id,
        metadata={'user_id': usuario.pk}
    )
