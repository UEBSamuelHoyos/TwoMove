# apps/users/services/auth_service.py

from django.contrib.auth import authenticate, login, logout

class AuthService:

    @staticmethod
    def iniciar_sesion(request, email, password):
        usuario = authenticate(request, username=email, password=password)
        if not usuario:
            return None, "Credenciales incorrectas"

        if usuario.estado != "activo":
            return None, "Cuenta no verificada"

        login(request, usuario)
        return usuario, None

    @staticmethod
    def cerrar_sesion(request):
        logout(request)
