from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from apps.admin_dashboard.models import Administrador


class AdminAuthService:
    """
    Servicio de autenticación para administradores del panel TwoMove.
    """

    @staticmethod
    def autenticar_admin(request, email, password):
        """
        Autentica un usuario solo si tiene perfil de administrador activo.
        """
        user = authenticate(request, username=email, password=password)
        if user is None:
            raise PermissionDenied("Credenciales inválidas.")

        try:
            admin = Administrador.objects.get(usuario=user)
        except Administrador.DoesNotExist:
            raise PermissionDenied("No tienes permisos para acceder al panel administrativo.")

        if not admin.activo:
            raise PermissionDenied("Tu cuenta de administrador está inactiva.")

        # Registrar acceso y loguear al usuario
        admin.registrar_acceso()
        login(request, user)
        return admin

    @staticmethod
    def cerrar_sesion(request):
        """
        Cierra la sesión actual del panel administrativo.
        """
        logout(request)
