from django.utils import timezone
from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from apps.rentals.models import Rental
# ⛓️ Lanza la simulación MQTT en background cuando inicia el viaje
from apps.iot.services.start_simulation_service import simulate_route_async


class TripStartService:
    """
    Servicio encargado de iniciar un viaje a partir de una reserva existente.

    Flujo al iniciar:
      1) Valida estado y código
      2) Cambia bici -> 'en_uso' y reserva -> 'activo'
      3) Registra hora de inicio
      4) Envía correo de confirmación
      5) 🚀 Dispara simulación IoT en background (OSRM + MQTT) para dibujar la ruta en el mapa
    """

    # -------------------------------------------------------------
    # 🔹 Inicio por usuario autenticado
    # -------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def start_trip_by_user(user_pk=None, codigo: str = ""):
        """
        Inicia el viaje buscando la reserva en estado 'reservado'
        perteneciente al usuario autenticado.
        """
        if user_pk is None:
            raise ValueError("Falta la PK del usuario autenticado.")
        if not codigo:
            raise ValueError("Debe proporcionar el código de desbloqueo.")

        codigo = codigo.strip()

        reservas_qs = (
            Rental.objects.select_related("bike", "usuario", "estacion_origen", "estacion_destino")
            .filter(usuario_id=user_pk, estado__iexact="reservado")
            .order_by("-creado_en")
        )

        total = reservas_qs.count()
        print(f"📦 Reservas encontradas para usuario {user_pk}: {total}")

        if total == 0:
            raise ValueError("No existe ninguna reserva en estado 'reservado' para este usuario.")
        if total > 1:
            raise ValueError("Existen múltiples reservas en estado 'reservado'. Contacte soporte.")

        rental = reservas_qs.first()
        return TripStartService._activate_rental(rental, codigo)

    # -------------------------------------------------------------
    # 🔹 Inicio legacy por ID explícito
    # -------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def start_trip(user, rental_id: int, codigo: str):
        """Inicia un viaje usando el ID de la reserva (modo clásico)."""
        try:
            rental = Rental.objects.select_related("bike", "usuario", "estacion_origen", "estacion_destino").get(
                pk=rental_id, usuario_id=getattr(user, "pk", None)
            )
        except Rental.DoesNotExist:
            raise ValueError("Reserva no encontrada o no pertenece al usuario.")

        return TripStartService._activate_rental(rental, codigo)

    # -------------------------------------------------------------
    # 🔹 Activación interna del viaje
    # -------------------------------------------------------------
    @staticmethod
    def _activate_rental(rental: Rental, codigo: str):
        """
        Valida el código de desbloqueo y activa la reserva:
          - Verifica estado actual 'reservado'
          - Comprueba código válido
          - Cambia estado de bicicleta y de reserva a 'activo'
          - Registra la hora de inicio
          - Envía correo de confirmación
          - 🚀 Lanza simulación IoT (OSRM + MQTT) en background
        """
        print(f"🧩 Validando inicio de rental #{rental.id}...")

        if not rental.estado or rental.estado.lower() != "reservado":
            raise ValueError(f"La reserva no está en estado 'reservado' (actual: {rental.estado}).")

        codigo_normalizado = (codigo or "").strip()
        valid_codes = set()

        if rental.codigo_desbloqueo:
            valid_codes.add(rental.codigo_desbloqueo.strip())
        if rental.bike_serial_reservada:
            valid_codes.add(rental.bike_serial_reservada.strip())

        print(f"🔐 Códigos válidos asociados a la reserva #{rental.id}: {valid_codes}")

        if codigo_normalizado not in valid_codes:
            raise ValueError(f"Código incorrecto. Código recibido: {codigo_normalizado}")

        # Obtener la bicicleta
        bike = rental.bike
        bike_serial = rental.bike_serial_reservada or getattr(bike, "numero_serie", "N/A")

        # Verificar estado de bicicleta
        if hasattr(bike, "estado") and bike.estado:
            estado_bike = bike.estado.lower().strip()
            if estado_bike not in ("disponible", "reservada", "reserved"):
                raise ValueError(f"La bicicleta no está disponible (estado actual: {bike.estado}).")
            print(f"✅ Estado de bicicleta aceptado: {bike.estado}")

        # Cambiar estados y registrar inicio
        print(f"🚴 Activando bicicleta {bike_serial} y reserva #{rental.id}...")

        if hasattr(bike, "estado"):
            bike.estado = "en_uso"
            bike.save(update_fields=["estado"])

        rental.estado = "activo"
        rental.hora_inicio = timezone.now()
        rental.save(update_fields=["estado", "hora_inicio"])

        print(f"✅ Viaje iniciado — Rental #{rental.id} | Bicicleta: {bike_serial}")

        # ✅ Enviar correo de confirmación
        TripStartService._enviar_correo_inicio(rental)

        # 🚀 Disparar simulación IoT en background (no bloquea la petición)
        try:
            if rental.estacion_origen and rental.estacion_destino:
                simulate_route_async(rental.id)
                print(f"📡 Telemetría simulada iniciada para rental #{rental.id}")
            else:
                print(f"⚠️ Rental #{rental.id} no tiene estaciones de origen/destino completas; no se lanza simulación.")
        except Exception as e:
            # No interrumpir el flujo del usuario por un fallo en la simulación
            print(f"⚠️ No se pudo iniciar la simulación IoT para rental #{rental.id}: {e}")

        return {
            "rental_id": rental.pk,
            "bike_serial": bike_serial,
            "estado": rental.estado,
            "hora_inicio": rental.hora_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "mensaje": "Viaje iniciado correctamente. Bicicleta desbloqueada.",
        }

    # -------------------------------------------------------------
    # 📧 Envío de correo: Confirmación de inicio de viaje
    # -------------------------------------------------------------
    @staticmethod
    def _enviar_correo_inicio(rental: Rental):
        """
        Envía un correo al usuario confirmando el inicio de su viaje.
        Usa el template: rentals/trip_started.html
        """
        try:
            usuario = rental.usuario
            context = {
                "usuario": usuario,
                "user": usuario,
                "hora_inicio": rental.hora_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                "bicicleta": rental.bike_serial_reservada or getattr(rental.bike, "numero_serie", ""),
                "estacion": rental.estacion_origen.nombre if rental.estacion_origen else "N/A",
                "SITE_NAME": "TwoMove",
            }

            html_content = render_to_string("rentals/trip_started.html", context)
            subject = f"🚴 Viaje iniciado – Bicicleta {context['bicicleta']}"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [usuario.email]

            msg = EmailMultiAlternatives(subject, "", from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            print(f"📩 Correo de inicio de viaje enviado a {usuario.email}")
        except Exception as e:
            print(f"⚠️ Error al enviar correo de inicio de viaje: {e}")
