# apps/users/services/user_info_service.py

from django.db.models import Sum
from django.utils import timezone
from apps.wallet.models import Wallet
from apps.rentals.models import Rental
from apps.payment.models import MetodoTarjeta
from apps.stations.models import Station
from apps.users.services.email_service import EmailService
from apps.users.models import CambioCredenciales, Usuario

class UserInfoService:

    @staticmethod
    def obtener_dashboard(user):
        wallet, _ = Wallet.objects.get_or_create(usuario=user)
        hoy = timezone.now()
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        viajes_mes = Rental.objects.filter(
            usuario=user,
            hora_inicio__gte=inicio_mes,
            estado="finalizado"
        ).count()

        minutos = Rental.objects.filter(
            usuario=user,
            estado="finalizado",
            duracion_minutos__isnull=False
        ).aggregate(total=Sum('duracion_minutos'))['total'] or 0

        horas = minutos // 60
        tiempo_total = f"{horas}h {minutos % 60}min"

        total_viajes = Rental.objects.filter(usuario=user, estado="finalizado").count()
        nivel = (
            "Nuevo" if total_viajes == 0 else
            "Principiante" if total_viajes < 5 else
            "Intermedio" if total_viajes < 20 else
            "Avanzado" if total_viajes < 50 else "Experto"
        )

        return {
            "wallet": wallet,
            "saldo_disponible": wallet.balance,
            "viajes_mes": viajes_mes,
            "tiempo_total": tiempo_total,
            "nivel": nivel,
            "pagos": MetodoTarjeta.objects.filter(usuario=user).order_by('-creado_en')[:5],
            "estaciones": Station.objects.all(),
        }

    @staticmethod
    def enviar_recordatorio_usuario(email):
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return False, "Correo no encontrado"

        mensaje = f"""
Hola {user.nombre},

Tu usuario es: {user.nombre} {user.apellido}
Email: {user.email}

Equipo TwoMove 🚲
"""
        EmailService.enviar_correo_simple(
            asunto="Recordatorio de usuario",
            mensaje=mensaje,
            destinatario=email
        )

        CambioCredenciales.objects.create(usuario=user, tipo_cambio='usuario')
        return True, None
