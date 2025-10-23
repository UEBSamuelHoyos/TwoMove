from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .services.wallet_service import WalletService
from apps.wallet.models import Wallet


@api_view(['GET'])
@login_required
def obtener_saldo(request):
    """
    Devuelve el saldo actual del usuario autenticado.
    """
    usuario = request.user
    wallet = WalletService.obtener_o_crear_wallet(usuario)
    return Response({
        'usuario': usuario.username,
        'saldo_actual': wallet.balance
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def recargar_wallet(request):
    """
    Endpoint que permite aumentar el saldo de una wallet (recarga).
    Usado por payment-service al recibir confirmación de Stripe.
    No requiere autenticación (llamado interno con usuario_id).
    """
    try:
        usuario_id = request.data.get("usuario_id")
        monto = request.data.get("monto")

        if not usuario_id or not monto:
            return Response({"error": "usuario_id y monto son requeridos."}, status=400)

        monto_decimal = Decimal(monto)
        if monto_decimal <= 0:
            return Response({"error": "El monto debe ser mayor a cero."}, status=400)

        # Crear o recuperar la wallet del usuario
        wallet = WalletService.obtener_o_crear_wallet_by_id(usuario_id)
        wallet.balance += monto_decimal
        wallet.save()

        return Response({
            "mensaje": "Recarga aplicada correctamente.",
            "nuevo_saldo": str(wallet.balance)
        }, status=200)

    except Wallet.DoesNotExist:
        return Response({"error": "Wallet no encontrada para este usuario."}, status=404)
    except Exception as e:
        return Response({"error": f"Error inesperado: {str(e)}"}, status=500)
