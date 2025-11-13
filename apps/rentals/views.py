from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.db import connection
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import json
from datetime import datetime

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
# 8️⃣ Historial de viajes
# ---------------------------------------------------------------
@login_required
def trip_history_view(request):
    """
    Vista para mostrar la página de historial de viajes.
    """
    return render(request, 'rentals/trip_history.html')


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
                "fecha_reserva": r.fecha_reserva.strftime("%Y-%m-%d") if r.fecha_reserva else r.creado_en.strftime("%Y-%m-%d"),
                "hora_reserva": r.hora_reserva.strftime("%H:%M") if r.hora_reserva else r.creado_en.strftime("%H:%M"),
                "metodo_pago": r.metodo_pago,
                "bike_serial_reservada": r.bike_serial_reservada or "",
                "estacion_origen": getattr(r.estacion_origen, "nombre", "") if r.estacion_origen else "",
                "estacion_destino": getattr(r.estacion_destino, "nombre", "") if hasattr(r, "estacion_destino") and r.estacion_destino else "",
                "costo_estimado": str(r.costo_estimado or ""),
            }
            for r in reservas
        ]
        return Response(data, status=status.HTTP_200_OK)

    # ----------------------------
    # Historial de viajes
    # ----------------------------
    @action(detail=False, methods=["get"], url_path="historial")
    def historial(self, request):
        """
        API para obtener el historial de viajes del usuario con filtros opcionales.
        
        Parámetros de query:
        - estado: filtrar por estado (finalizado, activo, cancelado)
        - tipo_viaje: filtrar por tipo (ultima_milla, recorrido_largo)
        - fecha: filtrar por fecha específica (formato: YYYY-MM-DD)
        - page: número de página (default: 1)
        - per_page: viajes por página (default: 10)
        """
        try:
            usuario = request.user
            
            # Obtener parámetros de filtro
            estado = request.GET.get('estado', None)
            tipo_viaje = request.GET.get('tipo_viaje', None)
            fecha = request.GET.get('fecha', None)
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 100))
            
            # Query base - TODOS los viajes del usuario
            queryset = Rental.objects.filter(
                usuario=usuario
            ).select_related(
                'estacion_origen',
                'estacion_destino',
                'bike'
            ).order_by('-creado_en')
            
            print(f"📊 Total de viajes del usuario {usuario.email}: {queryset.count()}")
            
            # Aplicar filtros solo si se especifican
            if estado:
                queryset = queryset.filter(estado=estado)
                print(f"🔍 Filtrado por estado '{estado}': {queryset.count()} viajes")
            
            if tipo_viaje:
                queryset = queryset.filter(tipo_viaje=tipo_viaje)
                print(f"🔍 Filtrado por tipo '{tipo_viaje}': {queryset.count()} viajes")
            
            if fecha:
                try:
                    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                    queryset = queryset.filter(creado_en__date=fecha_obj)
                    print(f"🔍 Filtrado por fecha '{fecha}': {queryset.count()} viajes")
                except ValueError:
                    print(f"⚠️ Fecha inválida: {fecha}")
                    pass
            
            # Contar total de registros
            total_viajes = queryset.count()
            
            # Calcular estadísticas solo de finalizados
            stats = Rental.objects.filter(
                usuario=usuario,
                estado='finalizado'
            ).aggregate(
                total_gastado=Sum('costo_total'),
                total_viajes_finalizados=Count('id')
            )
            
            # Paginación
            start = (page - 1) * per_page
            end = start + per_page
            viajes_pagina = queryset[start:end]
            
            # Serializar datos
            viajes_data = []
            for viaje in viajes_pagina:
                # Calcular duración si está finalizado
                duracion_minutos = None
                if viaje.hora_fin and viaje.hora_inicio:
                    duracion = (viaje.hora_fin - viaje.hora_inicio).total_seconds() / 60
                    duracion_minutos = round(duracion, 1)
                
                viaje_dict = {
                    'id': viaje.id,
                    'estado': viaje.estado,
                    'tipo_viaje': viaje.tipo_viaje,
                    'estacion_origen': viaje.estacion_origen.nombre if viaje.estacion_origen else 'N/A',
                    'estacion_destino': viaje.estacion_destino.nombre if viaje.estacion_destino else 'N/A',
                    'bike_serial_reservada': viaje.bike_serial_reservada or (viaje.bike.numero_serie if viaje.bike else 'N/A'),
                    'metodo_pago': viaje.metodo_pago or 'N/A',
                    'costo_total': float(viaje.costo_total) if viaje.costo_total else 0,
                    'duracion_minutos': duracion_minutos or 0,
                    'hora_inicio': viaje.hora_inicio.isoformat() if viaje.hora_inicio else viaje.creado_en.isoformat(),
                    'hora_fin': viaje.hora_fin.isoformat() if viaje.hora_fin else None,
                }
                viajes_data.append(viaje_dict)
            
            print(f"✅ Enviando {len(viajes_data)} viajes al frontend")
            
            # Preparar respuesta
            response_data = {
                'viajes': viajes_data,
                'estadisticas': {
                    'total_viajes': stats['total_viajes_finalizados'] or 0,
                    'total_gastado': float(stats['total_gastado']) if stats['total_gastado'] else 0,
                },
                'paginacion': {
                    'pagina_actual': page,
                    'total_paginas': max(1, (total_viajes + per_page - 1) // per_page),
                    'total_registros': total_viajes,
                    'por_pagina': per_page,
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Error en historial: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': 'Error al obtener el historial de viajes'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ----------------------------
    # Estadísticas del usuario
    # ----------------------------
    @action(detail=False, methods=["get"], url_path="estadisticas")
    def estadisticas(self, request):
        """
        Devuelve estadísticas del usuario: viajes del mes, tiempo total, etc.
        """
        usuario = request.user
        ahora = timezone.now()
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Viajes finalizados del usuario
        viajes_finalizados = Rental.objects.filter(
            usuario=usuario,
            estado="finalizado"
        )
        
        # Viajes este mes
        viajes_mes = viajes_finalizados.filter(
            hora_fin__gte=inicio_mes
        ).count()
        
        # Tiempo total (calcular desde hora_inicio y hora_fin)
        tiempo_total_minutos = 0
        for viaje in viajes_finalizados:
            if viaje.hora_inicio and viaje.hora_fin:
                duracion = (viaje.hora_fin - viaje.hora_inicio).total_seconds() / 60
                tiempo_total_minutos += duracion
        
        # Convertir minutos a horas y minutos
        horas = int(tiempo_total_minutos // 60)
        minutos = int(tiempo_total_minutos % 60)
        tiempo_total_texto = f"{horas}h {minutos}min"
        
        # Determinar nivel según cantidad de viajes
        total_viajes = viajes_finalizados.count()
        if total_viajes == 0:
            nivel = "Nuevo"
        elif total_viajes < 5:
            nivel = "Principiante"
        elif total_viajes < 20:
            nivel = "Intermedio"
        elif total_viajes < 50:
            nivel = "Avanzado"
        else:
            nivel = "Experto"
        
        return Response({
            "viajes_mes": viajes_mes,
            "tiempo_total": tiempo_total_texto,
            "tiempo_total_minutos": int(tiempo_total_minutos),
            "nivel": nivel,
            "total_viajes": total_viajes,
        }, status=status.HTTP_200_OK)

    # ----------------------------
    # Estadísticas detalladas
    # ----------------------------
    @action(detail=False, methods=["get"], url_path="estadisticas_detalladas")
    def estadisticas_detalladas(self, request):
        """
        API para obtener estadísticas detalladas del usuario.
        """
        try:
            usuario = request.user
            
            # Estadísticas generales
            viajes_finalizados = Rental.objects.filter(
                usuario=usuario,
                estado='finalizado'
            )
            
            total_viajes = viajes_finalizados.count()
            total_gastado = viajes_finalizados.aggregate(
                total=Sum('costo_total')
            )['total'] or 0
            
            # Viajes por tipo
            viajes_por_tipo = viajes_finalizados.values('tipo_viaje').annotate(
                cantidad=Count('id')
            )
            
            # Estación más utilizada como origen
            estacion_favorita = viajes_finalizados.values(
                'estacion_origen__nombre'
            ).annotate(
                cantidad=Count('id')
            ).order_by('-cantidad').first()
            
            # Duración promedio
            duraciones = []
            for viaje in viajes_finalizados:
                if viaje.hora_fin and viaje.hora_inicio:
                    duracion = (viaje.hora_fin - viaje.hora_inicio).total_seconds() / 60
                    duraciones.append(duracion)
            
            duracion_promedio = sum(duraciones) / len(duraciones) if duraciones else 0
            
            response_data = {
                'total_viajes': total_viajes,
                'total_gastado': float(total_gastado),
                'viajes_por_tipo': {
                    item['tipo_viaje']: item['cantidad'] 
                    for item in viajes_por_tipo
                },
                'estacion_favorita': estacion_favorita['estacion_origen__nombre'] if estacion_favorita else None,
                'duracion_promedio_minutos': round(duracion_promedio, 1),
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Error en estadisticas_detalladas: {e}")
            return Response(
                {'error': 'Error al obtener estadísticas'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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