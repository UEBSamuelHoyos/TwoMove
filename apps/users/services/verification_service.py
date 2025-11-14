# apps/users/services/verification_service.py

from apps.users.models import Usuario

class VerificationService:

    @staticmethod
    def verificar_usuario(email, codigo):
        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.codigo_verificacion == codigo:
                usuario.estado = 'activo'
                usuario.codigo_verificacion = None
                usuario.save()
                return True, None
            else:
                return False, "Código incorrecto"
        except Usuario.DoesNotExist:
            return False, "Usuario no encontrado"
