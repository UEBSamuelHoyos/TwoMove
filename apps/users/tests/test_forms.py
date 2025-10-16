from django.test import TestCase
from apps.users.forms import RegistroForm, VerificacionForm
from apps.users.models import Usuario


# ======================================
# 🔹 PRUEBAS PARA RegistroForm
# ======================================

class RegistroFormTest(TestCase):

    def test_form_valido(self):
        """Formulario válido con contraseñas iguales."""
        form_data = {
            'nombre': 'Samuel',
            'apellido': 'Hoyos',
            'email': 'samuel@test.com',
            'celular': '3001234567',
            'contrasena': 'clave123',
            'confirmar_contrasena': 'clave123',
        }
        form = RegistroForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.check_password('clave123'))  # Verifica hasheo
        self.assertEqual(user.nombre, 'Samuel')

    def test_form_contrasenas_diferentes(self):
        """Formulario inválido si las contraseñas no coinciden."""
        form_data = {
            'nombre': 'Laura',
            'apellido': 'Ramírez',
            'email': 'laura@test.com',
            'celular': '3007654321',
            'contrasena': 'clave123',
            'confirmar_contrasena': 'diferente',
        }
        form = RegistroForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Las contraseñas no coinciden.', form.errors['__all__'])

    def test_form_faltan_campos(self):
        """Formulario inválido si faltan campos obligatorios."""
        form_data = {
            'nombre': 'Carlos',
            'email': 'carlos@test.com',
            'contrasena': 'clave123',
            'confirmar_contrasena': 'clave123',
        }
        form = RegistroForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('apellido', form.errors)
        self.assertIn('celular', form.errors)



class VerificacionFormTest(TestCase):

    def test_form_valido(self):
        """Formulario válido con email y código de 6 dígitos."""
        form_data = {
            'email': 'verificar@test.com',
            'codigo': '123456'
        }
        form = VerificacionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_codigo_mas_largo(self):
        """Formulario inválido si el código tiene más de 6 caracteres."""
        form_data = {
            'email': 'verificar@test.com',
            'codigo': '1234567'
        }
        form = VerificacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)

    def test_email_invalido(self):
        """Formulario inválido si el email no es válido."""
        form_data = {
            'email': 'no-es-un-email',
            'codigo': '123456'
        }
        form = VerificacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
