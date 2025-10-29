from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Rental
from .services.reservation_service import ReservationService
from .services.cancellation_service import CancellationService
from .serializers import RentalSerializer


# ---------------------------------------------------------------
# 1️⃣ Vista principal (pantalla base)
# ---------------------------------------------------------------
def index(request):
    """Página inicial del módulo de arrendamientos."""
    return render(request, "rentals/index.html")


# ---------------------------------------------------------------
# 2️⃣ Vista HTML de prueba para el flujo de reserva
# ---------------------------------------------------------------
class ReservationTestView(TemplateView):
    """Muestra el formulario HTML para probar el flujo de reserva."""
    template_name = "rentals/reservation_test.html"


# ---------------------------------------------------------------
# 3️⃣ Vista HTML para probar cancelación desde navegador
# ---------------------------------------------------------------
class CancelReservationTestView(TemplateView):
    """Muestra el formulario HTML para cancelar reservas mediante el endpoint cancel_general."""
    template_name = "rentals/cancel_reservation_test.html"


# ---------------------------------------------------------------
# 4️⃣ Vista HTML (manual) para cancelar una reserva específica por ID
# ---------------------------------------------------------------
@login_required
def cancel_reservation_view(request, rental_id):
    """Página HTML para cancelar una reserva existente (método clásico por ID)."""
    rental = get_object_or_404(Rental, pk=rental_id, usuario=request.user)

    if request.method == "POST":
        reason = request.POST.get("reason", "")
        try:
            result = CancellationService.cancel_reservation(
                user=request.user,
                rental_id=rental_id,
                reason=reason
            )
            messages.success(request, f"Reserva #{result['rental_id']} cancelada exitosamente.")
            return redirect("rentals:cancel_reservation", rental_id=rental.id)
        except Exception as e:
            messages.error(request, f"Error al cancelar la reserva: {e}")

    return render(request, "rentals/cancel_reservation.html", {"rental": rental})


# ---------------------------------------------------------------
# 5️⃣ API REST principal para gestionar arrendamientos
# ---------------------------------------------------------------
class RentalViewSet(viewsets.ModelViewSet):
    """API principal para gestionar arrendamientos (crear, cancelar, listar)."""
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]

    # ----------------------------
    # Crear reserva
    # ----------------------------
    @action(detail=False, methods=["post"], url_path="reserve", permission_classes=[IsAuthenticated])
    def reserve(self, request):
        """Crea una nueva reserva usando el servicio de negocio."""
        usuario = request.user
        data = request.data

        try:
            rental = ReservationService.create_reservation(
                usuario=usuario,
                estacion_origen_id=data.get("estacion_origen_id"),
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
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # Cancelar reserva por ID
    # ----------------------------
    @action(detail=True, methods=["post"], url_path="cancel", permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Cancela una reserva específica por ID."""
        try:
            result = CancellationService.cancel_reservation(
                user=request.user,
                rental_id=pk,
                reason=request.data.get("reason", "")
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # Cancelar reserva general
    # ----------------------------
    @action(detail=False, methods=["post"], url_path="cancel_general", permission_classes=[IsAuthenticated])
    def cancel_general(self, request):
        """Cancela una reserva sin usar el ID en la URL (se envía en el body JSON)."""
        usuario = request.user
        data = request.data
        rental_id = data.get("rental_id")
        reason = data.get("reason", "")

        if not rental_id:
            return Response({"detail": "Debe enviar 'rental_id'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = CancellationService.cancel_reservation(
                user=usuario,
                rental_id=rental_id,
                reason=reason
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # Listar reservas activas del usuario autenticado
    # ----------------------------
    @action(detail=False, methods=["get"], url_path="mis_reservas", permission_classes=[IsAuthenticated])
    def mis_reservas(self, request):
        """
        Devuelve las reservas activas del usuario autenticado.
        Compatible con modelo de usuario sin campo 'id'.
        """
        usuario = request.user
        print(f"🔍 Usuario autenticado: {usuario}")

        # ✅ Usa relación directa (no .id)
        reservas = Rental.objects.filter(
            usuario=usuario
        ).filter(
            Q(estado__iexact="reservado") | Q(estado__iexact="activo")
        ).order_by("-creado_en")

        print(f"📦 Reservas encontradas: {reservas.count()}")

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
                "costo_estimado": str(r.costo_estimado or ""),
            }
            for r in reservas
        ]

        return Response(data, status=status.HTTP_200_OK)
