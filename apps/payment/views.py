#views.py
from django.conf import settings
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages  # Para mensajes flash

from .services.recargar_saldo_service import RecargarSaldoService
from .services.stripe_service import crear_setup_intent
from .models import MetodoTarjeta

import stripe
import requests
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


# --- VISTAS HTML --- #

def menu_pagos(request):
    return render(request, 'payment/menu_pagos.html')


@login_required
def agregar_tarjeta_view(request):
    usuario = request.user
    setup_intent = crear_setup_intent(usuario)

    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': setup_intent.client_secret,
    }

    return render(request, 'payment/agregar_tarjeta.html', context)


@csrf_protect
@login_required
def recargar_saldo_view(request):
    """
    Vista HTML con formulario para recargar saldo y mostrar el resultado.
    """
    context = {}
    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            servicio = RecargarSaldoService(request.user, amount)
            resultado = servicio.crear_payment_intent()

            if resultado["status"] == "succeeded":
                context["mensaje"] = f"Tu recarga de ${resultado['amount']} COP fue procesada exitosamente."
            else:
                context["error"] = f"Tu recarga quedó en estado: {resultado['status']}."

        except Exception as e:
            context["error"] = str(e)

    return render(request, 'payment/recargar_saldo.html', context)


@csrf_exempt
def confirmar_recarga_view(request):
    status_pago = request.GET.get('status', 'pending')
    monto = request.GET.get('amount', '0')

    context = {
        'status_pago': status_pago,
        'monto': monto,
    }
    return render(request, 'payment/confirmar_recarga.html', context)


def eliminar_tarjeta_view(request):
    return render(request, 'payment/eliminar_tarjeta.html')


@api_view(['POST'])
@login_required
def guardar_tarjeta(request):
    """
    Guarda la tarjeta usando el PaymentMethod ya creado desde Stripe Elements.
    """
    try:
        usuario = request.user
        payment_method_id = request.data.get('payment_method_id')

        # Recuperar el PaymentMethod desde Stripe
        metodo = stripe.PaymentMethod.retrieve(payment_method_id)

        # Verifica que el método tenga customer ya asociado
        customer_id = metodo.get("customer")
        if not customer_id:
            raise Exception("❌ El método de pago no tiene un cliente (customer_id) asociado en Stripe.")

        # Guardar en base de datos
        MetodoTarjeta.objects.update_or_create(
            usuario=usuario,
            stripe_payment_method_id=payment_method_id,
            defaults={
                "stripe_customer_id": customer_id,
                "brand": metodo['card']['brand'],
                "last4": metodo['card']['last4'],
                "exp_month": metodo['card']['exp_month'],
                "exp_year": metodo['card']['exp_year']
            }
        )

        return Response({'mensaje': '✅ Tarjeta registrada correctamente.'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@login_required
def recargar_saldo_api(request):
    """
    API REST para recargar saldo desde frontend móvil u otras apps.
    Permite especificar qué tarjeta (payment_method_id) se usará.
    """
    try:
        usuario = request.user
        amount = request.data.get('amount')
        payment_method_id = request.data.get('payment_method_id')

        # Validaciones básicas
        if not amount or float(amount) <= 0:
            return Response({'error': 'Debe especificar un monto válido.'}, status=400)

        if not payment_method_id:
            return Response({'error': 'Debe especificar el ID del método de pago.'}, status=400)

        # Crear el servicio de recarga con la tarjeta elegida
        servicio = RecargarSaldoService(usuario, amount, payment_method_id)
        resultado = servicio.crear_payment_intent()

        return Response({
            'mensaje': 'Recarga procesada correctamente.',
            'estado': resultado['status'],
            'monto': resultado['amount'],
            'currency': resultado['currency'],
            'intent_id': resultado['intent_id'],
            'stripe_created': resultado['stripe_created']
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def recargar_saldo_view(request):
    """
    Vista HTML con formulario para recargar saldo.
    Ahora permite seleccionar entre múltiples tarjetas registradas.
    """
    context = {}
    tarjetas = MetodoTarjeta.objects.filter(usuario=request.user)

    if request.method == "POST":
        amount = request.POST.get("amount")
        payment_method_id = request.POST.get("payment_method_id")

        try:
            servicio = RecargarSaldoService(request.user, amount, payment_method_id)
            resultado = servicio.crear_payment_intent()

            if resultado["status"] == "succeeded":
                context["mensaje"] = f"Tu recarga de ${resultado['amount']} COP fue procesada exitosamente."
            else:
                context["error"] = f"Tu recarga quedó en estado: {resultado['status']}."

        except Exception as e:
            context["error"] = str(e)

    context["tarjetas"] = tarjetas
    return render(request, 'payment/recargar_saldo.html', context)


@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    """
    Webhook de Stripe que recibe confirmaciones de pago.
    Llama a los servicios de transacciones y wallet.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return Response({'error': str(e)}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        user_id = intent['metadata'].get('user_id')
        email = intent['metadata'].get('email')
        amount = Decimal(intent['amount']) / 100
        intent_id = intent['id']

        try:
            # Llamar a transactions
            trans_resp = requests.post(
                f"{settings.TRANSACTIONS_SERVICE_URL}/crear/",
                headers={"Authorization": f"Bearer {settings.INTERNAL_AUTH_TOKEN}"},
                json={
                    "usuario_id": user_id,
                    "tipo": "RECARGA",
                    "monto": str(amount),
                    "descripcion": f"Recarga desde tarjeta para {email}",
                    "referencia_externa": intent_id
                }
            )
            trans_resp.raise_for_status()

            # Llamar a wallet
            wallet_resp = requests.patch(
                f"{settings.WALLET_SERVICE_URL}/topup/",
                headers={"Authorization": f"Bearer {settings.INTERNAL_AUTH_TOKEN}"},
                json={
                    "usuario_id": user_id,
                    "monto": str(amount)
                }
            )
            wallet_resp.raise_for_status()

        except requests.RequestException as e:
            return Response({'error': f'Error notificando a servicios internos: {str(e)}'}, status=500)

    return Response({'status': 'ok'}, status=200)




@login_required
def eliminar_tarjeta_view(request):
    """
    Muestra todas las tarjetas del usuario y permite eliminarlas individualmente.
    """
    tarjetas = MetodoTarjeta.objects.filter(usuario=request.user)

    # Si no hay tarjetas, solo renderiza el mensaje
    if not tarjetas.exists():
        return render(request, 'payment/eliminar_tarjeta.html', {'tarjetas': []})

    return render(request, 'payment/eliminar_tarjeta.html', {'tarjetas': tarjetas})


@login_required
def eliminar_tarjeta_id_view(request, tarjeta_id):
    try:
        tarjeta = MetodoTarjeta.objects.get(id=tarjeta_id, usuario=request.user)
        
        # Opcional: Detach de Stripe también
        try:
            stripe.PaymentMethod.detach(tarjeta.stripe_payment_method_id)
        except Exception as e:
            messages.warning(request, f"No se pudo desvincular de Stripe: {e}")

        tarjeta.delete()
        messages.success(request, "Tarjeta eliminada correctamente.")
    except MetodoTarjeta.DoesNotExist:
        messages.error(request, "No se encontró la tarjeta seleccionada.")

    return redirect('eliminar_tarjeta_view')



