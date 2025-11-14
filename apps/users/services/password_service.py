# apps/users/services/password_service.py

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone

from apps.users.models import Usuario, CambioCredenciales
from apps.users.services.email_service import EmailService


class PasswordService:

    @staticmethod
    def enviar_enlace_recuperacion(request, email):
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return False, "No existe una cuenta con ese correo."

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        enlace = request.build_absolute_uri(f"/usuarios/restablecer/{uid}/{token}/")

        EmailService.enviar_correo_html(
            asunto="Restablecer contraseña - TwoMove 🚲",
            template='users/email_recuperar_contrasena.html',
            context={'user': user, 'enlace': enlace, 'year': timezone.now().year},
            destinatario=email
        )

        return True, None

    @staticmethod
    def restablecer(uidb64, token, password1, password2):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except:
            return None, "Enlace inválido"

        if not default_token_generator.check_token(user, token):
            return None, "Token inválido"

        if password1 != password2:
            return None, "Las contraseñas no coinciden"

        user.set_password(password1)
        user.save()
        CambioCredenciales.objects.create(usuario=user, tipo_cambio='contraseña')

        return user, None
