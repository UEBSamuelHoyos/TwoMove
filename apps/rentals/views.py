from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import connection
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Rental
from .serializers import RentalSerializer
from .services.reservation_service import ReservationService
from .services.cancellation_service import CancellationService
from .services.trip_start_service import TripStartService
from .services.trip_end_service import TripEndService


# ---------------------------------------------------------------
# 1️⃣ Vista principal
# ---------------------------------------------------------------
def index(request):
    return render(request, "rentals/index.html")


# ---------------------------------------------------------------
# 2️⃣ Prueba HTML reserva
# ---------------------------------------------------------------
class ReservationTestView(TemplateView):
    template_name = "rentals/reservation_test.html"


# ---------------------------------------------------------------
# 3️⃣ Prueba HTML cancelación
# ---------------------------------------------------------------
class CancelReservationTestView(TemplateView):
    template_name = "rentals/cancel_reservation_test.html"


# ---------------------------------------------------------------
# 4️⃣ Cancelar reserva específica
# ---------------------------------------------------------------
@login_required
def cancel_reservation_view(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id, usuario_id=request.user.pk)
    if request.method == "POST":
        reason = request.POST.get("reason", "")
        try:
            result = CancellationService.cancel_reservation(
                user=request.user, rental_id=rental_id, reason=reason
            )
            messages.success(request, f"Reserva #{result['rental_id']} cancelada exitosamente.")
            return redirect("rentals:cancel_reservation", rental_id=rental.id)
        except Exception as e:
            messages.error(request, f"Error al cancelar la reserva: {e}")

    return render(request, "rentals/cancel_reservation.html", {"rental": rental})


# ---------------------------------------------------------------
# 5️⃣ Prueba HTML inicio de viaje
# ---------------------------------------------------------------
class StartTripTestView(TemplateView):
    template_name = "rentals/start_trip_test.html"


# ---------------------------------------------------------------
# 6️⃣ API principal arrendamientos
# ---------------------------------------------------------------
class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]

    # ----------------------------
    # Crear reserva
    # ----------------------------
    @action(detail=False, methods=["post"], url_path="reserve")
    def reserve(self, request):
        usuario = request.user
        data = request.data
        try:
            rental = ReservationService.create_reservation(
                usuario=usuario,
                estacion_origen_id=data.get("estacion_origen_id"),
                estacion_destino_id=data.get("estacion_destino_id"),
                tipo_bicicleta=data.get("tipo_bicicleta"),
                tipo_viaje=data.get("tipo_viaje"),
                metodo_pago=data.get("metodo_pago"),
            )
            return Response({
                "status": "ok",
                "rental_id": rental.id,
                "bike_serial_reservada": rental.bike_serial_reservada,
                "bike_dock_reservado": rental.bike_dock_reservado,
                "codigo_desbloqueo": rental.codigo_desbloqueo,
                "metodo_pago": rental.metodo_pago,
                "fecha_reserva": getattr(rental, "fecha_reserva", None),
                "hora_reserva": getattr(rental, "hora_reserva", None),
                "estacion_origen": getattr(rental.estacion_origen, "nombre", ""),
                "estacion_destino": getattr(rental.estacion_destino, "nombre", ""),
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # Iniciar viaje
    # ----------------------------
    @action(detail=False, methods=["post"], url_path="start_by_user")
    def start_by_user(self, request):
        codigo = (request.data.get("codigo") or "").strip()
        if not codigo:
            return Response({"detail": "Debe ingresar el código."}, status=status.HTTP_400_BAD_REQUEST)
        usuario = request.user
        try:
            result = TripStartService.start_trip_by_user(user_pk=usuario.pk, codigo=codigo)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print("❌ Error inicio de viaje:", str(e))
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # ✅ Finalizar viaje
    # ----------------------------
    @action(detail=False, methods=["post"], url_path="end_trip")
    def end_trip(self, request):
        """
        Finaliza el viaje activo y genera factura.
        Body: { "rental_id": int, "estacion_destino_id": int (opcional) }
        """
        usuario = request.user
        data = request.data
        rental_id = data.get("rental_id")
        estacion_destino_id = data.get("estacion_destino_id")

        if not rental_id:
            return Response({"detail": "Debe enviar rental_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = TripEndService.end_trip(usuario, rental_id, estacion_destino_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print("❌ Error finalizando viaje:", e)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # Cancelar reserva por ID
    # ----------------------------
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        try:
            result = CancellationService.cancel_reservation(
                user=request.user, rental_id=pk, reason=request.data.get("reason", "")
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # Cancelar reserva general
    # ----------------------------
    @action(detail=False, methods=["post"], url_path="cancel_general")
    def cancel_general(self, request):
        usuario = request.user
        data = request.data
        rental_id = data.get("rental_id")
        reason = data.get("reason", "")
        if not rental_id:
            return Response({"detail": "Debe enviar rental_id."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = CancellationService.cancel_reservation(
                user=usuario, rental_id=rental_id, reason=reason
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # Mis reservas
    # ----------------------------
    @action(detail=False, methods=["get"], url_path="mis_reservas")
    def mis_reservas(self, request):
        usuario_pk = getattr(request.user, "pk", None)
        reservas = (
            Rental.objects.filter(usuario_id=usuario_pk)
            .filter(Q(estado__iexact="reservado") | Q(estado__iexact="activo"))
            .order_by("-creado_en")
        )
        data = [
            {
                "id": r.pk,
                "tipo_viaje": r.tipo_viaje,
                "estado": r.estado,
                "fecha_reserva": r.fecha_reserva.strftime("%Y-%m-%d") if r.fecha_reserva else "",
                "hora_reserva": r.hora_reserva.strftime("%H:%M") if r.hora_reserva else "",
                "metodo_pago": r.metodo_pago,
                "bike_serial_reservada": r.bike_serial_reservada or "",
                "estacion_origen": getattr(r.estacion_origen, "nombre", "") if r.estacion_origen else "",
                "estacion_destino": getattr(r.estacion_destino, "nombre", "") if hasattr(r, "estacion_destino") and r.estacion_destino else "",
                "costo_estimado": str(r.costo_estimado or ""),
            }
            for r in reservas
        ]
        return Response(data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------
# 7️⃣ Finalizar viaje (HTML)
# ---------------------------------------------------------------
@method_decorator(login_required, name='dispatch')
class TripEndPageView(View):
    """Renderiza la página visual para finalizar el viaje"""
    def get(self, request):
        return render(request, "rentals/trip_end.html")


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class TripEndAPI(View):
    """Endpoint API para cerrar el viaje y generar factura"""
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            estacion_destino_id = data.get("estacion_destino_id")
            rental_id = data.get("rental_id")

            if not rental_id:
                return JsonResponse({"error": "Debe especificar el ID del viaje."}, status=400)

            resultado = TripEndService.end_trip(
                usuario=request.user,
                rental_id=rental_id,
                estacion_destino_id=estacion_destino_id,
            )

            return JsonResponse({
                "success": True,
                "mensaje": resultado["mensaje"],
                "costo_total": resultado["costo_total"],
                "duracion_minutos": resultado["duracion_minutos"],
                "estado_bicicleta": resultado["estado_bicicleta"],
            }, status=200)

        except Exception as e:
            print(f"❌ Error al finalizar viaje: {e}")
            return JsonResponse({"error": str(e)}, status=400)
