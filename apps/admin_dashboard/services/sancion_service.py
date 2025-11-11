from django.utils import timezone
from django.db import transaction
from apps.admin_dashboard.models import Sancion
from apps.users.models import Usuario


class SancionService:
    """
    Servicio para gestionar las sanciones de los usuarios.
    Incluye creación, levantamiento y verificación de estado.
    """

    # ============================================================
    # 🚫 CREAR SANCIÓN
    # ============================================================
    @staticmethod
    @transaction.atomic
    def crear_sancion(usuario: Usuario, motivo: str, descripcion: str = "", dias: int = 3, admin=None):
        """
        Crea una nueva sanción para un usuario y actualiza su estado.
        """
        fecha_fin = timezone.now() + timezone.timedelta(days=dias)

        sancion = Sancion.objects.create(
            usuario=usuario,
            motivo=motivo,
            descripcion=descripcion or "",
            fecha_inicio=timezone.now(),
            fecha_fin=fecha_fin,
            activa=True,
            creada_por=getattr(admin, "email", "Sistema"),
        )

        # Cambiar estado del usuario
        usuario.estado = "sancionado"
        usuario.save()

        print(f"⚠️ Sanción creada para {usuario.email}: {motivo} ({dias} días)")
        return sancion

    # ============================================================
    # ✅ LEVANTAR SANCIÓN
    # ============================================================
    @staticmethod
    @transaction.atomic
    def levantar_sancion(sancion: Sancion):
        """
        Marca una sanción como inactiva y, si el usuario no tiene más sanciones activas,
        lo reactiva automáticamente.
        """
        sancion.activa = False
        sancion.save()

        # Verificar si hay otras sanciones activas
        if not Sancion.objects.filter(usuario=sancion.usuario, activa=True).exists():
            sancion.usuario.estado = "activo"
            sancion.usuario.save()
            print(f"✅ Usuario {sancion.usuario.email} reactivado (sin sanciones activas).")
        else:
            print(f"🕓 Usuario {sancion.usuario.email} aún tiene sanciones activas.")

        return sancion

    # ============================================================
    # 🔍 VERIFICAR ESTADO DE USUARIO
    # ============================================================
    @staticmethod
    def usuario_sancionado(usuario: Usuario) -> bool:
        """
        Retorna True si el usuario tiene alguna sanción activa.
        """
        activo = Sancion.objects.filter(usuario=usuario, activa=True).exists()
        if activo:
            print(f"🚫 Usuario {usuario.email} actualmente sancionado.")
        return activo

    # ============================================================
    # 🧾 OBTENER HISTORIAL
    # ============================================================
    @staticmethod
    def historial_usuario(usuario: Usuario):
        """
        Devuelve todas las sanciones del usuario, más recientes primero.
        """
        sanciones = Sancion.objects.filter(usuario=usuario).order_by("-fecha_inicio")
        print(f"📋 Historial de sanciones para {usuario.email}: {sanciones.count()} registro(s).")
        return sanciones
