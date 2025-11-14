# apps/users/services/registration_service.py

from apps.users.forms import RegistroForm
from apps.users.services.email_service import EmailService

class RegistrationService:

    @staticmethod
    def registrar_usuario(request):
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            usuario.generar_codigo_verificacion()

            EmailService.enviar_correo_simple(
                asunto="Código de verificación - TwoMove 🚲",
                mensaje=f"Tu código es: {usuario.codigo_verificacion}",
                destinatario=usuario.email
            )
            return usuario, None
        else:
            return None, form
