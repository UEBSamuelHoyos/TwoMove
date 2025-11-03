from django.db import transaction
from django.core.exceptions import ValidationError
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
      1️⃣ Validar usuario y sanciones
      2️⃣ Verificar disponibilidad en estación
      3️⃣ Validar método de pago (wallet o tarjeta)
      4️⃣ Crear Rental
      5️⃣ Asignar bicicleta
      6️⃣ Registrar transacción (si aplica)
      7️⃣ Notificar al usuario
    """

    @staticmethod
    @transaction.atomic
    def create_reservation(
        usuario,
        estacion_origen_id: int,
        tipo_bicicleta: str,        # "electric" | "manual"
        tipo_viaje: str,            # "ultima_milla" | "recorrido_largo"
        metodo_pago: str            # "wallet" | "card"
    ):
        print("🚴 Iniciando proceso de reserva...")

        # 1️⃣ Validar sanciones
        if getattr(usuario, "tiene_multas", False):
            raise ValidationError("No puedes reservar porque tienes multas activas.")
        if getattr(usuario, "saldo_negativo", False):
            raise ValidationError("No puedes reservar porque tu saldo está en negativo.")

        # 2️⃣ Validar si ya tiene reserva activa
        if Rental.objects.filter(usuario=usuario, estado__in=["reservado", "activo"]).exists():
            raise ValidationError("Ya tienes una reserva o viaje activo.")

        # 3️⃣ Validar estación
        try:
            estacion = Station.objects.get(id=estacion_origen_id)
        except Station.DoesNotExist:
            raise ValidationError("La estación seleccionada no existe.")

        print(f"📍 Estación seleccionada: {estacion.nombre}")

        # 4️⃣ Buscar bicicleta disponible
        bikes = Bike.objects.filter(
            station=estacion,
            tipo=tipo_bicicleta,
            estado="available"
        )

        # ⚡ Solo bicicletas eléctricas con batería suficiente
        if tipo_bicicleta == "electric" and hasattr(Bike, "bateria_porcentaje"):
            bikes = bikes.filter(bateria_porcentaje__gte=40)

        bike = bikes.first()
        if not bike:
            raise ValidationError("No hay bicicletas disponibles del tipo solicitado en esta estación.")
        print(f"🚲 Bicicleta asignada: {bike.numero_serie} ({bike.tipo})")

        # 5️⃣ Validar método de pago
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

        # 6️⃣ Generar código de desbloqueo
        codigo_desbloqueo = secrets.token_hex(3).upper()  # Ejemplo: 'A3F9D1'
        print(f"🔐 Código de desbloqueo generado: {codigo_desbloqueo}")

        # 7️⃣ Crear reserva
        rental = Rental.objects.create(
            usuario=usuario,
            bike=bike,
            estacion_origen=estacion,
            tipo_viaje=tipo_viaje,
            metodo_pago=metodo_pago,
            estado="reservado",
            bike_serial_reservada=bike.numero_serie,
            bike_dock_reservado=getattr(bike, "dock_position", None),
            codigo_desbloqueo=codigo_desbloqueo,
        )
        print(f"📝 Reserva creada con ID #{rental.id}")

        # 8️⃣ Marcar bicicleta como reservada
        bike.estado = "reserved"
        bike.save()
        print(f"🔒 Bicicleta {bike.numero_serie} marcada como reservada.")

        # 9️⃣ Registrar transacción y actualizar saldo si paga con wallet
        if metodo_pago == "wallet" and wallet:
            wallet.balance -= costo_estimado
            wallet.save()

            WalletTransaccion.objects.create(
                wallet=wallet,
                tipo="PAGO",
                monto=-costo_estimado,
                descripcion=f"Reserva anticipada de bicicleta ({tipo_viaje})",
                saldo_resultante=wallet.balance,
                referencia_externa=f"rental_{rental.id}"
            )
            print(f"💵 Transacción registrada correctamente. Nuevo saldo: {wallet.balance} COP")

        # 🔟 Notificación (simulada por consola)
        ReservationService._notificar_reserva(usuario, rental)

        print("✅ Proceso de reserva completado correctamente.")
        return rental

    # --------------------------------------------------------------------

    @staticmethod
    def _notificar_reserva(usuario, rental):
        """
        Notificación simulada (correo o app).
        """
        print(f"""
        ✅ RESERVA CONFIRMADA
        Usuario: {usuario.email}
        Bicicleta: {rental.bike_serial_reservada} ({rental.bike.get_tipo_display()})
        Estación: {rental.estacion_origen.nombre}
        Dock: {rental.bike_dock_reservado or 'N/A'}
        Código de desbloqueo: {rental.codigo_desbloqueo}
        Método de pago: {rental.metodo_pago}
        """)
