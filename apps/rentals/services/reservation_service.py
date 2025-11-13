from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from decimal import Decimal
import secrets

from apps.rentals.models import Rental
from apps.bikes.models import Bike
from apps.stations.models import Station
from apps.transactions.models import WalletTransaccion
from apps.wallet.models import Wallet
from apps.payment.models import MetodoTarjeta


class ReservationService:
    """
    Flujo completo de reserva:
      1) Validar usuario y sanciones
      2) Verificar disponibilidad en estación
      3) Validar método de pago (wallet o tarjeta)
      4) Crear Rental (con estación origen y destino)
      5) Asignar bicicleta
      6) Registrar transacción (si aplica)
      7) Enviar correo de confirmación
    """

    @staticmethod
    @transaction.atomic
    def create_reservation(
        usuario,
        estacion_origen_id: int,
        tipo_bicicleta: str,        # "electric" | "manual"
        tipo_viaje: str,            # "ultima_milla" | "recorrido_largo"
        metodo_pago: str,           # "wallet" | "card"
        estacion_destino_id: int    # 👈 NUEVO: destino obligatorio
    ):
        print("🚴 Iniciando proceso de reserva...")

        # 1) Validar sanciones
        if getattr(usuario, "tiene_multas", False):
            raise ValidationError("No puedes reservar porque tienes multas activas.")
        if getattr(usuario, "saldo_negativo", False):
            raise ValidationError("No puedes reservar porque tu saldo está en negativo.")

        # 2) Validar si ya tiene reserva activa
        if Rental.objects.filter(usuario=usuario, estado__in=["reservado", "activo"]).exists():
            raise ValidationError("Ya tienes una reserva o viaje activo.")

        # 3) Validar estaciones (origen y destino)
        try:
            estacion_origen = Station.objects.get(id=estacion_origen_id)
        except Station.DoesNotExist:
            raise ValidationError("La estación de origen seleccionada no existe.")

        if not estacion_destino_id:
            raise ValidationError("Debes seleccionar una estación de destino.")

        try:
            estacion_destino = Station.objects.get(id=estacion_destino_id)
        except Station.DoesNotExist:
            raise ValidationError("La estación de destino seleccionada no existe.")

        if estacion_origen.id == estacion_destino.id:
            raise ValidationError("La estación de destino debe ser diferente a la estación de origen.")

        print(f"📍 Origen: {estacion_origen.nombre}  →  Destino: {estacion_destino.nombre}")

        # 4) Buscar bicicleta disponible en origen
        bikes = Bike.objects.filter(
            station=estacion_origen,
            tipo=tipo_bicicleta,
            estado="available"
        )
        if tipo_bicicleta == "electric" and hasattr(Bike, "bateria_porcentaje"):
            bikes = bikes.filter(bateria_porcentaje__gte=40)

        bike = bikes.first()
        if not bike:
            raise ValidationError("No hay bicicletas disponibles del tipo solicitado en la estación de origen.")
        print(f"🚲 Bicicleta asignada: {getattr(bike, 'numero_serie', getattr(bike, 'serial', 'N/A'))} ({getattr(bike, 'tipo', 'N/A')})")

        # 5) Validar método de pago
        costo_estimado = Decimal("17500") if tipo_viaje == "ultima_milla" else Decimal("25000")
        print(f"💰 Costo estimado: {costo_estimado} COP")

        wallet = None
        if metodo_pago == "wallet":
            wallet = Wallet.objects.filter(usuario=usuario).first()
            if not wallet:
                raise ValidationError("No tienes una billetera activa.")
            if wallet.balance < costo_estimado:
                raise ValidationError(f"Saldo insuficiente. Tienes {wallet.balance} COP disponibles.")
            print(f"✅ Wallet válida. Saldo actual: {wallet.balance} COP")
        elif metodo_pago == "card":
            tarjetas = MetodoTarjeta.objects.filter(usuario=usuario)
            if not tarjetas.exists():
                raise ValidationError("No tienes una tarjeta registrada.")
            tarjeta = tarjetas.first()
            print(f"💳 Tarjeta detectada: {tarjeta.brand.upper()} ****{tarjeta.last4}")
        else:
            raise ValidationError("Método de pago no soportado.")

        # 6) Generar código de desbloqueo
        codigo_desbloqueo = secrets.token_hex(3).upper()  # p.ej. 'A3F9D1'
        print(f"🔐 Código de desbloqueo generado: {codigo_desbloqueo}")

        # 7) Crear reserva (incluyendo estación destino)
        bike_serial = getattr(bike, "numero_serie", getattr(bike, "serial", None))
        dock_pos = getattr(bike, "dock_position", None)

        rental = Rental.objects.create(
            usuario=usuario,
            bike=bike,
            estacion_origen=estacion_origen,
            estacion_destino=estacion_destino,   # 👈 NUEVO
            tipo_viaje=tipo_viaje,
            metodo_pago=metodo_pago,
            estado="reservado",
            bike_serial_reservada=bike_serial,
            bike_dock_reservado=dock_pos,
            codigo_desbloqueo=codigo_desbloqueo,
            costo_estimado=costo_estimado,       # opcional si quieres dejar trazado
        )
        print(f"📝 Reserva creada con ID #{rental.id}")

        # 8) Marcar bicicleta como reservada
        bike.estado = "reserved"
        bike.save(update_fields=["estado"])

        # 9) Registrar transacción y actualizar saldo si paga con wallet
        if metodo_pago == "wallet" and wallet:
            wallet.balance -= costo_estimado
            wallet.save(update_fields=["balance"])
            WalletTransaccion.objects.create(
                wallet=wallet,
                tipo="PAGO",
                monto=-costo_estimado,
                descripcion=f"Reserva anticipada de bicicleta ({tipo_viaje})",
                saldo_resultante=wallet.balance,
                referencia_externa=f"rental_{rental.id}"
            )
            print(f"💵 Transacción registrada. Nuevo saldo: {wallet.balance} COP")

        # 10) Enviar correo de confirmación
        ReservationService._enviar_correo_confirmacion(usuario, rental)

        print("✅ Proceso de reserva completado correctamente.")
        return rental

    # --------------------------------------------------------------------
    @staticmethod
    def _enviar_correo_confirmacion(usuario, rental):
        """Envía un correo HTML al usuario confirmando su reserva (plantilla rentals/reservation_confirmed.html)."""
        try:
            subject = "✅ Tu reserva de bicicleta ha sido confirmada"
            from_email = None  # usa DEFAULT_FROM_EMAIL
            to = [usuario.email]

            # Contexto para el template
            ctx = {
    "usuario": usuario,
    "rental": rental,
    "codigo": rental.codigo_desbloqueo,
    "estacion_origen": getattr(rental.estacion_origen, "nombre", "N/A"),  # Por si acaso
            "estacion_destino": getattr(rental.estacion_destino, "nombre", "N/A") if rental.estacion_destino else "N/A",
            "bicicleta": rental.bike_serial_reservada or "Por asignar",
    "tipo_viaje": rental.tipo_viaje,
    "metodo_pago": rental.metodo_pago,
    "now": rental.creado_en,  # 👈 AGREGAR: para el footer del email
}

            html_content = render_to_string("rentals/reservation_confirmed.html", ctx)

            # Texto plano de respaldo
            text_content = (
                f"Hola {getattr(usuario, 'nombre', usuario.email)}.\n\n"
                f"Tu reserva ha sido confirmada.\n"
                 f"Origen: {ctx['estacion_origen']}\n"
            f"Destino: {ctx['estacion_destino']}\n"
            f"Bicicleta: {ctx['bicicleta']}\n"
                f"Código de desbloqueo: {ctx['codigo']}\n"
                f"Método de pago: {ctx['metodo_pago']}\n"
                "¡Buen viaje!"
            )

            email = EmailMultiAlternatives(subject, text_content, from_email, to)
            email.attach_alternative(html_content, "text/html")
            email.send()

            print(f"📩 Correo de confirmación enviado a {usuario.email}")

        except Exception as e:
            print(f"⚠️ Error al enviar correo de confirmación: {e}")
