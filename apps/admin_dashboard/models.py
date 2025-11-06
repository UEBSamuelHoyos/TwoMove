from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.users.models import Usuario


# ============================================================
# 👨‍💻 ADMINISTRADOR
# ============================================================
class Administrador(models.Model):
    """
    Representa a un administrador del sistema TwoMove,
    con acceso al panel de control.
    """

    ROLES = [
        ("superadmin", "Super Administrador"),
        ("operador", "Operador de campo"),
        ("analista", "Analista de datos"),
        ("soporte", "Soporte técnico"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_admin"
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default="operador"
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Teléfono de contacto del administrador."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Determina si el administrador tiene acceso al panel."
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del perfil de administrador."
    )

    ultimo_acceso = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Última fecha en que inició sesión en el panel."
    )

    def registrar_acceso(self):
        """Actualiza la fecha de último acceso."""
        self.ultimo_acceso = timezone.now()
        self.save(update_fields=["ultimo_acceso"])

    def __str__(self):
        return f"{self.usuario.email} ({self.get_rol_display()})"

    class Meta:
        verbose_name = "Administrador del sistema"
        verbose_name_plural = "Administradores del sistema"
        ordering = ["-creado_en"]


# ============================================================
# 🚫 SANCIÓN
# ============================================================
class Sancion(models.Model):
    """
    Registra las sanciones aplicadas a los usuarios por incumplimientos
    dentro del sistema TwoMove.
    """

    MOTIVOS = [
        ("no_devolucion", "No devolvió la bicicleta"),
        ("daño_bicicleta", "Daño al equipo o mal uso"),
        ("pago_pendiente", "Pago pendiente"),
        ("comportamiento", "Comportamiento inapropiado"),
        ("otros", "Otros"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="sanciones",
        help_text="Usuario sancionado."
    )

    motivo = models.CharField(
        max_length=50,
        choices=MOTIVOS,
        help_text="Motivo principal de la sanción."
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada de la falta o incidente."
    )

    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha en que inicia la sanción."
    )

    fecha_fin = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha en que termina la sanción (si aplica)."
    )

    activa = models.BooleanField(
        default=True,
        help_text="Indica si la sanción sigue activa."
    )

    creada_por = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Correo o nombre del administrador que aplicó la sanción."
    )

    creada_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha en que se registró la sanción."
    )

    actualizada_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última modificación de la sanción."
    )

    class Meta:
        verbose_name = "Sanción de usuario"
        verbose_name_plural = "Sanciones de usuarios"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        estado = "Activa" if self.activa else "Inactiva"
        return f"{self.usuario.email} - {self.get_motivo_display()} ({estado})"

    @property
    def dias_restantes(self):
        """Calcula los días restantes de la sanción, si tiene fecha fin."""
        if not self.fecha_fin:
            return "Indefinida"
        dias = (self.fecha_fin - timezone.now()).days
        return max(dias, 0)

    def levantar(self):
        """Desactiva la sanción y, si no hay más sanciones activas, reactiva el usuario."""
        self.activa = False
        self.save(update_fields=["activa"])
        if not Sancion.objects.filter(usuario=self.usuario, activa=True).exists():
            self.usuario.estado = "activo"
            self.usuario.save()
