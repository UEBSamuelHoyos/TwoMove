from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

from apps.transactions.services.transaction_service import TransactionService
from apps.wallet.models import Wallet


@api_view(['POST'])
def crear_transaccion(request):
    """
    Recibe datos desde payment-service y crea una transacción en la wallet del usuario.
    No usa serializer para responder.
    """
    try:
        usuario_id = request.data.get("usuario_id")
        tipo = request.data.get("tipo")  # RECARGA, PAGO, etc.
        monto = request.data.get("monto")
        descripcion = request.data.get("descripcion", "")
        referencia_externa = request.data.get("referencia_externa", None)

        # Validación básica
        if not usuario_id or not tipo or not monto:
            return Response(
                {"error": "Faltan campos obligatorios: usuario_id, tipo, monto."},
                status=400
            )

        monto_decimal = Decimal(monto)

        # Obtener wallet
        wallet = Wallet.objects.get(usuario_id=usuario_id)

        # Registrar la transacción
        transaccion = TransactionService.registrar_movimiento(
            wallet, tipo, monto_decimal, descripcion
        )

        # Guardar referencia externa (si aplica)
        if referencia_externa:
            transaccion.referencia_externa = referencia_externa
            transaccion.save()

        # Respuesta manual (sin serializer)
        return Response({
            "transaccion_id": str(transaccion.id),
            "tipo": transaccion.tipo,
            "monto": str(transaccion.monto),
            "saldo_resultante": str(transaccion.saldo_resultante),
            "descripcion": transaccion.descripcion,
            "fecha": transaccion.creado_en.strftime("%Y-%m-%d %H:%M:%S"),
            "referencia_externa": transaccion.referencia_externa
        }, status=201)

    except Wallet.DoesNotExist:
        return Response({"error": "Wallet no encontrada para este usuario."}, status=404)
    except ValueError as ve:
        return Response({"error": str(ve)}, status=402)  # saldo insuficiente
    except Exception as e:
        return Response({"error": f"Error inesperado: {str(e)}"}, status=500)
